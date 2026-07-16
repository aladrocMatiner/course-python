"""Deterministic Circuit Breaker example driven by an injected fake clock."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from enum import Enum
import math
from typing import TypeVar


T = TypeVar("T")
FAILURE_THRESHOLD = 3
COOLDOWN_SECONDS = 1.0


def _finite_number(value: object, code: str, *, positive: bool) -> float:
    """Return a finite built-in number while rejecting booleans explicitly."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(code)
    try:
        number = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(code) from error
    if not math.isfinite(number) or (number <= 0 if positive else number < 0):
        raise ValueError(code)
    return number


class TransientFailure(Exception):
    """A negative observation about dependency health."""


class PermanentFailure(Exception):
    """A responsive dependency result, even though the request was rejected."""


class CircuitOpen(Exception):
    """The circuit denied a dependency call locally."""


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


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


class ScriptedDependency:
    """Inject a finite series of values or failures."""

    def __init__(self, outcomes: Sequence[object]) -> None:
        if not outcomes:
            raise ValueError("at least one outcome is required")
        self._outcomes = list(outcomes)
        self.calls = 0

    def __call__(self) -> object:
        if self.calls >= len(self._outcomes):
            raise AssertionError("the finite dependency script was exhausted")
        outcome = self._outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class CircuitBreaker:
    """Gate calls for one dependency-health domain."""

    def __init__(
        self,
        clock: Callable[[], float],
        *,
        failure_threshold: int = FAILURE_THRESHOLD,
        cooldown_seconds: float = COOLDOWN_SECONDS,
    ) -> None:
        if (
            isinstance(failure_threshold, bool)
            or not isinstance(failure_threshold, int)
            or failure_threshold < 1
        ):
            raise ValueError("failure_threshold_must_be_positive_int")
        cooldown = _finite_number(
            cooldown_seconds,
            "cooldown_must_be_finite_positive",
            positive=True,
        )
        if not callable(clock):
            raise ValueError("clock_must_be_callable")
        self._clock = clock
        self._last_clock = self._read_clock()
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self._opened_at: float | None = None
        self._probe_in_flight = False

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

    def _request_permission(self) -> bool:
        """Return whether this call owns the exclusive HALF_OPEN probe."""

        if self.state is CircuitState.CLOSED:
            return False
        if self.state is CircuitState.HALF_OPEN or self._probe_in_flight:
            raise CircuitOpen("probe_in_progress")
        assert self._opened_at is not None
        if self._now() - self._opened_at < self.cooldown_seconds:
            raise CircuitOpen("circuit_open")
        self.state = CircuitState.HALF_OPEN
        self._probe_in_flight = True
        return True

    def _positive(self) -> None:
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self._opened_at = None
        self._probe_in_flight = False

    def _negative(self) -> None:
        if self.state is CircuitState.HALF_OPEN:
            try:
                opened_at = self._now()
            except ValueError:
                # Release the exclusive probe even when the injected clock is bad.
                self.state = CircuitState.OPEN
                self._probe_in_flight = False
                raise
            self.state = CircuitState.OPEN
            self._opened_at = opened_at
            self._probe_in_flight = False
            return
        next_failures = self.consecutive_failures + 1
        if next_failures >= self.failure_threshold:
            opened_at = self._now()
            self.state = CircuitState.OPEN
            self._opened_at = opened_at
        self.consecutive_failures = next_failures

    def _neutral(self, owned_probe: bool) -> None:
        if owned_probe:
            # Preserve the old eligibility time: a local failure did not test health.
            self.state = CircuitState.OPEN
            self._probe_in_flight = False

    def call(self, operation: Callable[[], T]) -> T:
        if not callable(operation):
            raise ValueError("operation_must_be_callable")
        owned_probe = self._request_permission()
        try:
            result = operation()
        except TransientFailure:
            self._negative()
            raise
        except PermanentFailure:
            self._positive()
            raise
        except BaseException:
            self._neutral(owned_probe)
            raise
        else:
            self._positive()
            return result


def main() -> None:
    clock = FakeClock()
    breaker = CircuitBreaker(clock)

    for number in range(1, FAILURE_THRESHOLD + 1):
        dependency = ScriptedDependency([TransientFailure("temporary")])
        try:
            breaker.call(dependency)
        except TransientFailure:
            print(
                f"negative={number} state={breaker.state.value} "
                f"dependency_calls={dependency.calls}"
            )

    blocked = ScriptedDependency(["should-not-run"])
    try:
        breaker.call(blocked)
    except CircuitOpen as error:
        print(f"boundary code={error} dependency_calls={blocked.calls}")

    clock.advance(COOLDOWN_SECONDS)
    failed_probe = ScriptedDependency([TransientFailure("probe_failed")])
    try:
        breaker.call(failed_probe)
    except TransientFailure:
        print(f"probe result=negative state={breaker.state.value}")

    clock.advance(COOLDOWN_SECONDS)
    successful_probe = ScriptedDependency(["healthy"])
    result = breaker.call(successful_probe)
    print(f"recovery result={result} state={breaker.state.value}")

    try:
        CircuitBreaker(clock, failure_threshold=True)
    except ValueError as error:
        print(f"config_boundary code={error} existing_state={breaker.state.value}")

    before = clock()
    try:
        clock.advance(float("nan"))
    except ValueError as error:
        print(f"clock_recovery code={error} unchanged={clock() == before}")


if __name__ == "__main__":
    main()
