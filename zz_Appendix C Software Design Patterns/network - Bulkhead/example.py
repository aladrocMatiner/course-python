"""Two bounded, independent admission compartments with fake time."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
import math


RUNNING_LIMIT = 1
WAITING_LIMIT = 1
ADMISSION_TIMEOUT_SECONDS = 0.05
MAX_CONFIGURED_RUNNING = 64
MAX_CONFIGURED_WAITING = 64
MAX_ADMISSION_TIMEOUT_SECONDS = 60.0
MAX_NAME_CHARACTERS = 64
MAX_REQUEST_ID_CHARACTERS = 64


def _bounded_int(value: object, code: str, *, minimum: int, maximum: int) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not minimum <= value <= maximum
    ):
        raise ValueError(code)
    return value


def _finite_number(value: object, code: str, *, positive: bool) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(code)
    try:
        number = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(code) from error
    if not math.isfinite(number) or (number <= 0 if positive else number < 0):
        raise ValueError(code)
    return number


def _bounded_text(value: object, code: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError(code)
    return value


class Overloaded(Exception):
    """The finite running and waiting capacity is already occupied."""


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self._now = _finite_number(
            start, "clock_start_must_be_finite_non_negative", positive=False
        )

    def __call__(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        step = _finite_number(
            seconds, "clock_advance_must_be_finite_positive", positive=True
        )
        updated = self._now + step
        if not math.isfinite(updated):
            raise ValueError("clock_value_must_remain_finite")
        self._now = updated


class Lease:
    def __init__(self, request_id: str, owner: "Bulkhead") -> None:
        self.request_id = request_id
        self._owner = owner
        self.released = False


class WaitingAdmission:
    def __init__(self, request_id: str, deadline: float) -> None:
        self.request_id = request_id
        self.deadline = deadline
        self.state = "waiting"


class Bulkhead:
    """One running lease plus one finite waiting slot."""

    def __init__(
        self,
        name: str,
        clock: Callable[[], float],
        *,
        running_limit: int = RUNNING_LIMIT,
        waiting_limit: int = WAITING_LIMIT,
        admission_timeout: float = ADMISSION_TIMEOUT_SECONDS,
    ) -> None:
        self.name = _bounded_text(
            name, "bulkhead_name_must_be_bounded_non_empty_text", MAX_NAME_CHARACTERS
        )
        checked_running = _bounded_int(
            running_limit,
            "running_limit_must_be_bounded_positive_int",
            minimum=1,
            maximum=MAX_CONFIGURED_RUNNING,
        )
        checked_waiting = _bounded_int(
            waiting_limit,
            "waiting_limit_must_be_bounded_non_negative_int",
            minimum=0,
            maximum=MAX_CONFIGURED_WAITING,
        )
        checked_timeout = _finite_number(
            admission_timeout,
            "admission_timeout_must_be_finite_positive",
            positive=True,
        )
        if checked_timeout > MAX_ADMISSION_TIMEOUT_SECONDS:
            raise ValueError("admission_timeout_exceeds_teaching_cap")
        if not callable(clock):
            raise ValueError("clock_must_be_callable")
        self._clock = clock
        self._last_clock = self._read_clock()
        self.running_limit = checked_running
        self.waiting_limit = checked_waiting
        self.admission_timeout = checked_timeout
        self._running: dict[str, Lease] = {}
        self._waiting: deque[WaitingAdmission] = deque(maxlen=max(1, checked_waiting))

    def _read_clock(self) -> float:
        return _finite_number(
            self._clock(), "clock_must_return_finite_number", positive=False
        )

    def _now(self) -> float:
        now = self._read_clock()
        if now < self._last_clock:
            raise ValueError("clock_must_be_monotonic")
        self._last_clock = now
        return now

    @property
    def running_count(self) -> int:
        return len(self._running)

    @property
    def waiting_count(self) -> int:
        return len(self._waiting)

    def expire_waiters(self) -> tuple[str, ...]:
        expired: list[str] = []
        now = self._now()
        retained: deque[WaitingAdmission] = deque(maxlen=max(1, self.waiting_limit))
        while self._waiting:
            admission = self._waiting.popleft()
            if now >= admission.deadline:
                admission.state = "timed_out"
                expired.append(admission.request_id)
            else:
                retained.append(admission)
        self._waiting = retained
        return tuple(expired)

    def admit(self, request_id: str) -> Lease | WaitingAdmission:
        checked_request_id = _bounded_text(
            request_id,
            "request_id_must_be_bounded_non_empty_text",
            MAX_REQUEST_ID_CHARACTERS,
        )
        self.expire_waiters()
        if checked_request_id in self._running or any(
            item.request_id == checked_request_id for item in self._waiting
        ):
            raise ValueError("request_id_must_be_unique_within_bulkhead")
        if len(self._running) < self.running_limit:
            lease = Lease(checked_request_id, self)
            self._running[checked_request_id] = lease
            return lease
        if len(self._waiting) >= self.waiting_limit:
            raise Overloaded(f"{self.name}:overloaded")
        deadline = self._now() + self.admission_timeout
        if not math.isfinite(deadline):
            raise ValueError("admission_deadline_must_remain_finite")
        admission = WaitingAdmission(checked_request_id, deadline=deadline)
        self._waiting.append(admission)
        return admission

    def release(self, lease: Lease) -> Lease | None:
        if not isinstance(lease, Lease) or lease._owner is not self:
            raise ValueError("lease_does_not_belong_to_bulkhead")
        if lease.released:
            return None
        owned = self._running.get(lease.request_id)
        if owned is not lease:
            raise ValueError("lease_is_not_active")
        # Validate time and remove expired waiters before mutating lease ownership.
        self.expire_waiters()
        lease.released = True
        del self._running[lease.request_id]
        if not self._waiting:
            return None
        admission = self._waiting.popleft()
        admission.state = "promoted"
        promoted = Lease(admission.request_id, self)
        self._running[promoted.request_id] = promoted
        return promoted


class BulkheadSet:
    """Separate local and remote failure domains."""

    def __init__(self, clock: Callable[[], float]) -> None:
        self.local = Bulkhead("local", clock)
        self.remote = Bulkhead("remote", clock)


def main() -> None:
    clock = FakeClock()
    compartments = BulkheadSet(clock)

    remote_running = compartments.remote.admit("remote-1")
    remote_waiting = compartments.remote.admit("remote-2")
    assert isinstance(remote_running, Lease)
    assert isinstance(remote_waiting, WaitingAdmission)

    try:
        compartments.remote.admit("remote-3")
    except Overloaded as error:
        print(
            f"boundary code={error} remote_running={compartments.remote.running_count} "
            f"remote_waiting={compartments.remote.waiting_count}"
        )

    local_running = compartments.local.admit("local-1")
    assert isinstance(local_running, Lease)
    print(
        f"isolation local={local_running.request_id} "
        f"remote={remote_running.request_id}"
    )

    clock.advance(ADMISSION_TIMEOUT_SECONDS)
    expired = compartments.remote.expire_waiters()
    compartments.remote.release(remote_running)
    compartments.local.release(local_running)
    recovered = compartments.remote.admit("remote-recovery")
    assert isinstance(recovered, Lease)
    print(
        f"recovery expired={list(expired)} admitted={recovered.request_id} "
        f"waiting={compartments.remote.waiting_count}"
    )

    compartments.remote.release(recovered)
    repeated_release = compartments.remote.release(recovered)
    print(
        f"cleanup repeated_release={repeated_release} running={compartments.remote.running_count}"
    )

    try:
        Bulkhead("invalid", clock, waiting_limit=True)
    except ValueError as error:
        print(
            f"config_boundary code={error} local_running={compartments.local.running_count}"
        )


if __name__ == "__main__":
    main()
