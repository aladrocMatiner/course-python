"""Two small asynchronous Bulkheads with bounded admission.

Capacity is deliberately separate from transport flow control.  These classes
limit application work only; they do not implement sockets or backpressure.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from .resilience import LocalPolicyError


T = TypeVar("T")


EXECUTION_LIMIT = 1
WAITING_LIMIT = 1
MAX_ADMISSION_TIMEOUT_SECONDS = 0.05


class Overloaded(LocalPolicyError):
    """Stable local admission result; it is neutral to dependency health."""

    def __init__(self, code: str = "overloaded") -> None:
        if code not in {"overloaded", "admission_timeout"}:
            raise ValueError("unsupported overload code")
        message = (
            "the compartment is full"
            if code == "overloaded"
            else "the queued admission expired"
        )
        super().__init__(code, message)


class BulkheadLease:
    """Idempotently releases one executing slot."""

    def __init__(self, bulkhead: Bulkhead) -> None:
        self._bulkhead = bulkhead
        self._released = False

    async def __aenter__(self) -> BulkheadLease:
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.release()

    def release(self) -> None:
        if self._released:
            return
        self._released = True
        self._bulkhead._release()


class Bulkhead:
    """One execution lease plus one expiring queued-admission slot."""

    execution_limit = EXECUTION_LIMIT
    waiting_limit = WAITING_LIMIT

    def __init__(
        self,
        name: str,
        clock: Callable[[], float],
        sleeper: Callable[[float], Awaitable[None]],
        *,
        admission_timeout: float = MAX_ADMISSION_TIMEOUT_SECONDS,
    ) -> None:
        if not name:
            raise ValueError("a Bulkhead needs a stable name")
        if admission_timeout <= 0:
            raise ValueError("admission_timeout must be positive")
        if admission_timeout > MAX_ADMISSION_TIMEOUT_SECONDS:
            raise ValueError(
                f"admission_timeout cannot exceed {MAX_ADMISSION_TIMEOUT_SECONDS}"
            )
        self.name = name
        self.clock = clock
        self.sleeper = sleeper
        self.admission_timeout = float(admission_timeout)
        self._executing = False
        self._waiter: asyncio.Future[None] | None = None
        self._timer: asyncio.Task[None] | None = None

    @property
    def executing(self) -> bool:
        return self._executing

    @property
    def waiting(self) -> bool:
        return self._waiter is not None and not self._waiter.done()

    @property
    def owned_task_count(self) -> int:
        return int(self._timer is not None and not self._timer.done())

    async def acquire(self, *, deadline: float) -> BulkheadLease:
        remaining = deadline - self.clock()
        if remaining <= 0:
            raise Overloaded("admission_timeout")

        if not self._executing:
            self._executing = True
            return BulkheadLease(self)

        if self._waiter is not None:
            raise Overloaded("overloaded")

        loop = asyncio.get_running_loop()
        waiter: asyncio.Future[None] = loop.create_future()
        timeout = min(self.admission_timeout, remaining)
        expires_at = self.clock() + timeout
        timer = asyncio.create_task(
            self.sleeper(timeout), name=f"patterns-{self.name}-admission-timeout"
        )
        self._waiter = waiter
        self._timer = timer
        try:
            done, _ = await asyncio.wait(
                (waiter, timer), return_when=asyncio.FIRST_COMPLETED
            )
            promoted = (
                waiter.done()
                and not waiter.cancelled()
                and self._waiter is not waiter
            )
            if timer in done or self.clock() >= expires_at:
                self._remove_waiter(waiter)
                await self._cancel_and_wait(timer)
                if promoted:
                    self._release()
                raise Overloaded("admission_timeout")

            if waiter in done:
                await self._cancel_and_wait(timer)
                return BulkheadLease(self)

            raise AssertionError("admission wait finished without a winner")
        except asyncio.CancelledError:
            promoted = waiter.done() and not waiter.cancelled() and self._waiter is not waiter
            self._remove_waiter(waiter)
            await self._cancel_and_wait(timer)
            if promoted:
                self._release()
            raise
        except BaseException:
            self._remove_waiter(waiter)
            await self._cancel_and_wait(timer)
            raise
        finally:
            if self._timer is timer:
                self._timer = None

    async def run(
        self,
        operation: Callable[[], Awaitable[T]],
        *,
        deadline: float,
    ) -> T:
        lease = await self.acquire(deadline=deadline)
        async with lease:
            return await operation()

    def _release(self) -> None:
        if not self._executing:
            return
        waiter = self._waiter
        if waiter is not None and not waiter.done():
            self._waiter = None
            waiter.set_result(None)
            return
        self._executing = False

    def _remove_waiter(self, waiter: asyncio.Future[None]) -> None:
        if self._waiter is waiter:
            self._waiter = None
        if not waiter.done():
            waiter.cancel()

    @staticmethod
    async def _cancel_and_wait(*tasks: asyncio.Task[None]) -> None:
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


class BulkheadSet:
    """The exact two independent failure domains used by the lesson."""

    NAMES = ("local", "remote")

    def __init__(
        self,
        clock: Callable[[], float],
        sleeper: Callable[[float], Awaitable[None]],
        *,
        admission_timeout: float = MAX_ADMISSION_TIMEOUT_SECONDS,
    ) -> None:
        self._bulkheads = {
            name: Bulkhead(
                name,
                clock,
                sleeper,
                admission_timeout=admission_timeout,
            )
            for name in self.NAMES
        }

    def __getitem__(self, name: str) -> Bulkhead:
        try:
            return self._bulkheads[name]
        except KeyError as exc:
            raise KeyError(f"unknown Bulkhead: {name}") from exc

    @property
    def owned_task_count(self) -> int:
        return sum(bulkhead.owned_task_count for bulkhead in self._bulkheads.values())

    async def run(
        self,
        name: str,
        operation: Callable[[], Awaitable[T]],
        *,
        deadline: float,
    ) -> T:
        return await self[name].run(operation, deadline=deadline)
