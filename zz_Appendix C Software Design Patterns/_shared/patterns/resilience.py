"""Deterministic Retry and Circuit Breaker examples for Appendix C.

The module deliberately owns no network transport.  Dependencies are injected
async callables, and time is injected so the companion tests never wait on the
wall clock.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from enum import Enum
from typing import TypeVar


T = TypeVar("T")


TOTAL_DEADLINE_SECONDS = 0.5
MAX_ATTEMPTS = 3
MAX_ATTEMPT_TIMEOUT_SECONDS = 0.1
PUBLISHED_BACKOFF_SECONDS = (0.05, 0.1)
FAILURE_THRESHOLD = 3
COOLDOWN_SECONDS = 1.0
_DEADLINE_EPSILON_SECONDS = 1e-9


class PolicyError(Exception):
    """Base error with a stable learner-visible code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class LocalPolicyError(PolicyError):
    """A local decision that is not evidence about dependency health."""


class ValidationError(LocalPolicyError):
    def __init__(self, message: str = "operation validation failed") -> None:
        super().__init__("validation_error", message)


class OperationDeadlineExceeded(LocalPolicyError):
    def __init__(self) -> None:
        super().__init__("deadline_exhausted", "the logical operation deadline expired")


class TransientDependencyError(PolicyError):
    def __init__(
        self,
        code: str = "transient_dependency",
        message: str = "the dependency failed transiently",
    ) -> None:
        super().__init__(code, message)


class PermanentDependencyError(PolicyError):
    def __init__(
        self,
        code: str = "permanent_dependency",
        message: str = "the dependency rejected the operation permanently",
    ) -> None:
        super().__init__(code, message)


class RetryExhausted(PolicyError):
    """Stable final error whose ``__cause__`` is the last transient failure."""

    def __init__(self, last_error: TransientDependencyError) -> None:
        super().__init__("retry_exhausted", "the bounded retry budget was exhausted")
        self.last_error = last_error


class CircuitOpen(LocalPolicyError):
    def __init__(self) -> None:
        super().__init__("circuit_open", "the dependency circuit is open")


class FakeClock:
    """Small monotonic clock advanced only by explicit test actions."""

    def __init__(self, start: float = 0.0) -> None:
        if start < 0:
            raise ValueError("clock start must be non-negative")
        self._now = float(start)

    def __call__(self) -> float:
        return self._now

    @property
    def now(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("a monotonic clock cannot move backwards")
        self._now += seconds


class FakeSleeper:
    """Injected sleeper with automatic or manually controlled fake time.

    Automatic mode advances after one event-loop turn.  That gives an immediate
    operation a chance to finish before its timeout task.  Manual mode is useful
    for capacity tests that need to inspect a registered waiter before expiry.
    """

    def __init__(self, clock: FakeClock, *, auto_advance: bool = True) -> None:
        self.clock = clock
        self.auto_advance = auto_advance
        self.requested: list[float] = []
        self.completed: list[float] = []
        self._pending: list[tuple[float, asyncio.Future[None]]] = []

    async def __call__(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("sleep duration must be non-negative")
        seconds = float(seconds)
        self.requested.append(seconds)
        if self.auto_advance:
            await asyncio.sleep(0)
            self.clock.advance(seconds)
            self.completed.append(seconds)
            return

        loop = asyncio.get_running_loop()
        future: asyncio.Future[None] = loop.create_future()
        entry = (self.clock() + seconds, future)
        self._pending.append(entry)
        try:
            await future
            self.completed.append(seconds)
        finally:
            if entry in self._pending:
                self._pending.remove(entry)

    def advance(self, seconds: float) -> None:
        """Advance manual time and wake every sleep whose deadline is due."""

        self.clock.advance(seconds)
        for deadline, future in tuple(self._pending):
            if deadline <= self.clock() and not future.done():
                future.set_result(None)

    @property
    def pending_count(self) -> int:
        return sum(not future.done() for _, future in self._pending)


class RetrySafety:
    """Declared reason why repeating an operation cannot duplicate an effect."""

    def __init__(
        self,
        *,
        side_effect_free: bool = False,
        idempotent: bool = False,
        idempotency_key: str | None = None,
        deduplication_enforced: bool = False,
    ) -> None:
        if deduplication_enforced and not idempotency_key:
            raise ValueError("enforced deduplication requires a non-empty key")
        self.side_effect_free = bool(side_effect_free)
        self.idempotent = bool(idempotent)
        self.idempotency_key = idempotency_key
        self.deduplication_enforced = bool(deduplication_enforced)

    @property
    def retry_safe(self) -> bool:
        return (
            self.side_effect_free
            or self.idempotent
            or bool(self.idempotency_key and self.deduplication_enforced)
        )

    @classmethod
    def read_only(cls) -> RetrySafety:
        return cls(side_effect_free=True)

    @classmethod
    def deduplicated(cls, key: str, *, enforced: bool) -> RetrySafety:
        return cls(idempotency_key=key, deduplication_enforced=enforced)


class RetryPolicy:
    """Bounded retry with one deadline shared by attempts and backoff."""

    def __init__(
        self,
        clock: Callable[[], float],
        sleeper: Callable[[float], Awaitable[None]],
        *,
        max_attempts: int = MAX_ATTEMPTS,
        attempt_timeout: float = MAX_ATTEMPT_TIMEOUT_SECONDS,
        total_deadline: float = TOTAL_DEADLINE_SECONDS,
        backoffs: tuple[float, ...] = PUBLISHED_BACKOFF_SECONDS,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if max_attempts > MAX_ATTEMPTS:
            raise ValueError(f"max_attempts cannot exceed {MAX_ATTEMPTS}")
        if attempt_timeout <= 0 or total_deadline <= 0:
            raise ValueError("timeouts must be positive")
        if attempt_timeout > MAX_ATTEMPT_TIMEOUT_SECONDS:
            raise ValueError(
                f"attempt_timeout cannot exceed {MAX_ATTEMPT_TIMEOUT_SECONDS}"
            )
        if total_deadline > TOTAL_DEADLINE_SECONDS:
            raise ValueError(
                f"total_deadline cannot exceed {TOTAL_DEADLINE_SECONDS}"
            )
        if len(backoffs) < max_attempts - 1 or any(delay < 0 for delay in backoffs):
            raise ValueError("backoffs must cover every possible retry")
        if (
            len(backoffs) > len(PUBLISHED_BACKOFF_SECONDS)
            or tuple(backoffs) != PUBLISHED_BACKOFF_SECONDS[: len(backoffs)]
        ):
            raise ValueError("backoffs must be the published 50/100 ms prefix")
        self.clock = clock
        self.sleeper = sleeper
        self.max_attempts = max_attempts
        self.attempt_timeout = float(attempt_timeout)
        self.total_deadline = float(total_deadline)
        self.backoffs = tuple(float(delay) for delay in backoffs)
        self._owned_tasks: set[asyncio.Task[object]] = set()

    def new_deadline(self) -> float:
        return self.clock() + self.total_deadline

    @property
    def owned_task_count(self) -> int:
        return sum(not task.done() for task in self._owned_tasks)

    async def execute(
        self,
        operation: Callable[[], Awaitable[T]],
        safety: RetrySafety,
        *,
        deadline: float | None = None,
        acquire_attempt_lease: (
            Callable[[float], Awaitable[AbstractAsyncContextManager[object]]] | None
        ) = None,
        _on_transient: Callable[[TransientDependencyError], None] | None = None,
    ) -> T:
        start = self.clock()
        hard_deadline = start + self.total_deadline
        operation_deadline = (
            hard_deadline if deadline is None else min(deadline, hard_deadline)
        )
        allowed_attempts = self.max_attempts if safety.retry_safe else 1
        last_transient: TransientDependencyError | None = None

        for attempt_index in range(allowed_attempts):
            remaining = operation_deadline - self.clock()
            if remaining <= 0:
                if last_transient is None:
                    raise OperationDeadlineExceeded()
                self._raise_exhausted(last_transient)

            try:
                async def timed_attempt() -> T:
                    remaining_after_gate = operation_deadline - self.clock()
                    if remaining_after_gate <= 0:
                        raise OperationDeadlineExceeded()
                    return await self._execute_once(
                        operation,
                        timeout=min(self.attempt_timeout, remaining_after_gate),
                    )

                if acquire_attempt_lease is None:
                    return await timed_attempt()
                lease = await acquire_attempt_lease(operation_deadline)
                async with lease:
                    return await timed_attempt()
            except asyncio.CancelledError:
                raise
            except PermanentDependencyError:
                raise
            except LocalPolicyError:
                if last_transient is None:
                    raise
                self._raise_exhausted(last_transient)
            except TransientDependencyError as exc:
                last_transient = exc
                if _on_transient is not None:
                    _on_transient(exc)

            if not safety.retry_safe:
                raise last_transient
            if attempt_index + 1 >= allowed_attempts:
                self._raise_exhausted(last_transient)

            backoff = self.backoffs[attempt_index]
            remaining = operation_deadline - self.clock()
            # Binary floating-point can represent an exact decimal boundary as
            # a few ulps below it (for example, 0.5 - 0.45).  Treat only that
            # numerical noise as an exact fit; a materially partial delay is
            # still forbidden.
            if backoff > remaining + _DEADLINE_EPSILON_SECONDS:
                self._raise_exhausted(last_transient)
            await self.sleeper(backoff)

        raise AssertionError("retry loop finished without a result")

    async def _execute_once(
        self,
        operation: Callable[[], Awaitable[T]],
        *,
        timeout: float,
    ) -> T:
        if timeout <= 0:
            raise OperationDeadlineExceeded()

        attempt_deadline = self.clock() + timeout
        operation_task = asyncio.create_task(operation(), name="patterns-dependency-attempt")
        timeout_task: asyncio.Task[None] | None = None
        self._owned_tasks.add(operation_task)
        try:
            # Let an immediately responsive dependency settle before registering
            # a fake timeout.  No monotonic time passes during this scheduler
            # turn, and a cancelled timeout can therefore never advance the
            # teaching clock or appear as a completed delay.
            await asyncio.sleep(0)
            if operation_task.done():
                if self.clock() > attempt_deadline + _DEADLINE_EPSILON_SECONDS:
                    await asyncio.gather(operation_task, return_exceptions=True)
                    raise self._attempt_timeout_error()
                return await operation_task

            timeout_task = asyncio.create_task(
                self.sleeper(timeout), name="patterns-attempt-timeout"
            )
            self._owned_tasks.add(timeout_task)
            done, _ = await asyncio.wait(
                (operation_task, timeout_task),
                return_when=asyncio.FIRST_COMPLETED,
            )
            if (
                operation_task in done
                and self.clock() <= attempt_deadline + _DEADLINE_EPSILON_SECONDS
            ):
                await self._cancel_and_wait(timeout_task)
                return await operation_task

            if operation_task in done:
                await self._cancel_and_wait(timeout_task)
                await asyncio.gather(operation_task, return_exceptions=True)
                raise self._attempt_timeout_error()

            await timeout_task
            await self._cancel_and_wait(operation_task)
            raise self._attempt_timeout_error()
        except BaseException:
            tasks: tuple[asyncio.Task[object], ...] = (
                (operation_task,)
                if timeout_task is None
                else (operation_task, timeout_task)
            )
            await self._cancel_and_wait(*tasks)
            raise
        finally:
            self._owned_tasks.discard(operation_task)
            if timeout_task is not None:
                self._owned_tasks.discard(timeout_task)

    @staticmethod
    async def _cancel_and_wait(*tasks: asyncio.Task[object]) -> None:
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    def _raise_exhausted(last_error: TransientDependencyError) -> None:
        raise RetryExhausted(last_error) from last_error

    @staticmethod
    def _attempt_timeout_error() -> TransientDependencyError:
        return TransientDependencyError(
            "attempt_timeout", "the dependency attempt exceeded its deadline"
        )


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """One availability circuit for one declared dependency-health domain."""

    def __init__(
        self,
        retry: RetryPolicy,
        clock: Callable[[], float],
        *,
        failure_threshold: int = FAILURE_THRESHOLD,
        cooldown: float = COOLDOWN_SECONDS,
    ) -> None:
        if failure_threshold != FAILURE_THRESHOLD:
            raise ValueError(f"failure_threshold must be {FAILURE_THRESHOLD}")
        if cooldown != COOLDOWN_SECONDS:
            raise ValueError(f"cooldown must be {COOLDOWN_SECONDS}")
        self.retry = retry
        self.clock = clock
        self.failure_threshold = failure_threshold
        self.cooldown = float(cooldown)
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.next_probe_at = 0.0

    @property
    def probe_in_flight(self) -> bool:
        return self.state is CircuitState.HALF_OPEN

    async def execute(
        self,
        operation: Callable[[], Awaitable[T]],
        safety: RetrySafety,
        *,
        deadline: float | None = None,
        validate: Callable[[], None] | None = None,
        acquire_attempt_lease: (
            Callable[[float], Awaitable[AbstractAsyncContextManager[object]]] | None
        ) = None,
    ) -> T:
        if validate is not None:
            validate()
        probe = self._request_permission()
        if probe:
            return await self._execute_probe(
                operation,
                deadline=deadline,
                acquire_attempt_lease=acquire_attempt_lease,
            )

        last_transient: TransientDependencyError | None = None

        def remember_transient(exc: TransientDependencyError) -> None:
            nonlocal last_transient
            last_transient = exc

        try:
            result = await self.retry.execute(
                operation,
                safety,
                deadline=deadline,
                acquire_attempt_lease=acquire_attempt_lease,
                _on_transient=remember_transient,
            )
        except asyncio.CancelledError:
            if last_transient is not None:
                self._record_negative()
            raise
        except PermanentDependencyError:
            self._close()
            raise
        except (TransientDependencyError, RetryExhausted):
            self._record_negative()
            raise
        except LocalPolicyError:
            raise
        else:
            self._close()
            return result

    def _request_permission(self) -> bool:
        if self.state is CircuitState.CLOSED:
            return False
        if self.state is CircuitState.HALF_OPEN:
            raise CircuitOpen()
        if self.clock() < self.next_probe_at:
            raise CircuitOpen()
        self.state = CircuitState.HALF_OPEN
        return True

    async def _execute_probe(
        self,
        operation: Callable[[], Awaitable[T]],
        *,
        deadline: float | None,
        acquire_attempt_lease: (
            Callable[[float], Awaitable[AbstractAsyncContextManager[object]]] | None
        ),
    ) -> T:
        hard_deadline = self.retry.new_deadline()
        operation_deadline = (
            hard_deadline if deadline is None else min(deadline, hard_deadline)
        )

        async def timed_probe() -> T:
            remaining = operation_deadline - self.clock()
            if remaining <= 0:
                raise OperationDeadlineExceeded()
            return await self.retry._execute_once(
                operation,
                timeout=min(self.retry.attempt_timeout, remaining),
            )

        try:
            if acquire_attempt_lease is None:
                result = await timed_probe()
            else:
                lease = await acquire_attempt_lease(operation_deadline)
                async with lease:
                    result = await timed_probe()
        except asyncio.CancelledError:
            self._return_to_open_without_cooldown()
            raise
        except PermanentDependencyError:
            self._close()
            raise
        except TransientDependencyError:
            self._open_with_fresh_cooldown()
            raise
        except LocalPolicyError:
            self._return_to_open_without_cooldown()
            raise
        except BaseException:
            self._return_to_open_without_cooldown()
            raise
        else:
            self._close()
            return result

    def _record_negative(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self._open_with_fresh_cooldown()

    def _open_with_fresh_cooldown(self) -> None:
        self.state = CircuitState.OPEN
        self.next_probe_at = self.clock() + self.cooldown

    def _return_to_open_without_cooldown(self) -> None:
        self.state = CircuitState.OPEN

    def _close(self) -> None:
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.next_probe_at = 0.0


class DeduplicatingDependency:
    """Fake side effect with optionally enforced key-based deduplication."""

    def __init__(
        self,
        *,
        enforces_deduplication: bool,
        lost_responses: int = 0,
    ) -> None:
        if lost_responses < 0:
            raise ValueError("lost_responses must be non-negative")
        self.enforces_deduplication = enforces_deduplication
        self._lost_responses = lost_responses
        self._stored: dict[str, str] = {}
        self.calls = 0
        self.effect_count = 0

    async def perform(self, key: str, value: str) -> str:
        self.calls += 1
        if self.enforces_deduplication and key in self._stored:
            result = self._stored[key]
        else:
            self.effect_count += 1
            result = f"stored:{value}"
            if self.enforces_deduplication:
                self._stored[key] = result

        if self._lost_responses:
            self._lost_responses -= 1
            raise TransientDependencyError(
                "response_lost", "the fake effect completed but its response was lost"
            )
        return result
