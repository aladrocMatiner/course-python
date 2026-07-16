"""Bounded, offline Retry example with injected failures and fake time."""

from __future__ import annotations

from collections.abc import Callable, Sequence
import math
from typing import Generic, TypeVar


T = TypeVar("T")

MAX_ATTEMPTS = 3
MAX_ATTEMPT_SECONDS = 0.10
TOTAL_BUDGET_SECONDS = 0.50
BACKOFF_SECONDS = (0.05, 0.10)
MAX_CONFIGURED_ATTEMPTS = 10
MAX_CONFIGURED_SECONDS = 60.0
MAX_IDEMPOTENCY_KEY_CHARACTERS = 64


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


class TransientFailure(Exception):
    """A dependency result that may be safe to try again."""


class PermanentFailure(Exception):
    """A dependency result that must not be retried automatically."""


class RetryNotSafe(Exception):
    """The first call failed transiently, but repetition is not justified."""


class RetryExhausted(Exception):
    """The attempt or total-time budget stopped further work."""

    def __init__(self, reason: str, attempts: int) -> None:
        super().__init__(f"retry_exhausted:{reason}")
        self.reason = reason
        self.attempts = attempts


class FakeClock:
    """A monotonic clock advanced only by this example's scripted actions."""

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


class RetrySafety:
    """Evidence that repeating an operation does not duplicate its effect."""

    def __init__(
        self,
        *,
        side_effect_free: bool = False,
        idempotent: bool = False,
        idempotency_key: str | None = None,
        deduplication_enforced: bool = False,
    ) -> None:
        for value, code in (
            (side_effect_free, "side_effect_free_must_be_bool"),
            (idempotent, "idempotent_must_be_bool"),
            (deduplication_enforced, "deduplication_enforced_must_be_bool"),
        ):
            if not isinstance(value, bool):
                raise ValueError(code)
        if idempotency_key is not None and (
            not isinstance(idempotency_key, str)
            or not idempotency_key
            or len(idempotency_key) > MAX_IDEMPOTENCY_KEY_CHARACTERS
        ):
            raise ValueError("idempotency_key_must_be_bounded_non_empty_text")
        self.side_effect_free = side_effect_free
        self.idempotent = idempotent
        self.idempotency_key = idempotency_key
        self.deduplication_enforced = deduplication_enforced

    def permits_repeat(self) -> bool:
        enforced_key = self.idempotency_key is not None and self.deduplication_enforced
        return self.side_effect_free or self.idempotent or enforced_key


class Outcome(Generic[T]):
    """One injected dependency outcome and its simulated duration."""

    def __init__(
        self,
        duration: float,
        value: T | None = None,
        error: Exception | None = None,
    ) -> None:
        self.duration = _finite_number(
            duration, "outcome_duration_must_be_finite_non_negative", positive=False
        )
        if self.duration > MAX_CONFIGURED_SECONDS:
            raise ValueError("outcome_duration_exceeds_teaching_cap")
        if error is not None and not isinstance(error, Exception):
            raise ValueError("outcome_error_must_be_exception_or_none")
        self.value = value
        self.error = error


class ScriptedDependency(Generic[T]):
    """Return or raise a finite script; never contact a real dependency."""

    def __init__(self, clock: FakeClock, outcomes: Sequence[Outcome[T]]) -> None:
        if not isinstance(clock, FakeClock):
            raise ValueError("script_clock_must_be_fake_clock")
        if not isinstance(outcomes, Sequence) or isinstance(outcomes, (str, bytes)):
            raise ValueError("outcomes_must_be_a_finite_sequence")
        if not 1 <= len(outcomes) <= MAX_CONFIGURED_ATTEMPTS:
            raise ValueError("outcome_count_exceeds_teaching_cap")
        if any(not isinstance(outcome, Outcome) for outcome in outcomes):
            raise ValueError("outcomes_must_contain_outcome_objects")
        self._clock = clock
        self._outcomes = list(outcomes)
        self.calls = 0

    def __call__(self, timeout: float) -> T:
        timeout_value = _finite_number(
            timeout, "attempt_timeout_must_be_finite_positive", positive=True
        )
        if self.calls >= len(self._outcomes):
            raise AssertionError("the finite dependency script was exhausted")
        outcome = self._outcomes[self.calls]
        self.calls += 1
        if outcome.duration > timeout_value:
            self._clock.advance(timeout_value)
            raise TransientFailure("attempt_timeout")
        if outcome.duration:
            self._clock.advance(outcome.duration)
        if outcome.error is not None:
            raise outcome.error
        return outcome.value  # type: ignore[return-value]


class RetryPolicy:
    """Repeat only transient, retry-safe work inside one finite budget."""

    def __init__(
        self,
        clock: FakeClock,
        *,
        max_attempts: int = MAX_ATTEMPTS,
        max_attempt_seconds: float = MAX_ATTEMPT_SECONDS,
        total_budget_seconds: float = TOTAL_BUDGET_SECONDS,
        backoffs: Sequence[float] = BACKOFF_SECONDS,
    ) -> None:
        if (
            isinstance(max_attempts, bool)
            or not isinstance(max_attempts, int)
            or not 1 <= max_attempts <= MAX_CONFIGURED_ATTEMPTS
        ):
            raise ValueError("max_attempts_must_be_bounded_positive_int")
        attempt_seconds = _finite_number(
            max_attempt_seconds,
            "max_attempt_seconds_must_be_finite_positive",
            positive=True,
        )
        total_seconds = _finite_number(
            total_budget_seconds,
            "total_budget_seconds_must_be_finite_positive",
            positive=True,
        )
        if (
            attempt_seconds > MAX_CONFIGURED_SECONDS
            or total_seconds > MAX_CONFIGURED_SECONDS
        ):
            raise ValueError("retry_time_exceeds_teaching_cap")
        if attempt_seconds > total_seconds:
            raise ValueError("attempt_timeout_must_not_exceed_total_budget")
        if not isinstance(backoffs, Sequence) or isinstance(backoffs, (str, bytes)):
            raise ValueError("backoffs_must_be_a_finite_sequence")
        if len(backoffs) != max_attempts - 1:
            raise ValueError("backoff_count_must_match_attempts")
        checked_backoffs = tuple(
            _finite_number(delay, "backoff_must_be_finite_non_negative", positive=False)
            for delay in backoffs
        )
        if any(delay > MAX_CONFIGURED_SECONDS for delay in checked_backoffs):
            raise ValueError("backoff_exceeds_teaching_cap")
        if not isinstance(clock, FakeClock):
            raise ValueError("policy_clock_must_be_fake_clock")
        self._clock = clock
        self._last_clock = self._read_clock()
        self.max_attempts = max_attempts
        self.max_attempt_seconds = attempt_seconds
        self.total_budget_seconds = total_seconds
        self.backoffs = checked_backoffs
        self.used_backoffs: list[float] = []

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

    def run(self, operation: Callable[[float], T], safety: RetrySafety) -> T:
        if not callable(operation):
            raise ValueError("operation_must_be_callable")
        if not isinstance(safety, RetrySafety):
            raise ValueError("safety_must_be_retry_safety")
        deadline = self._now() + self.total_budget_seconds
        if not math.isfinite(deadline):
            raise ValueError("deadline_must_remain_finite")
        self.used_backoffs = []
        last_transient: TransientFailure | None = None

        for attempt in range(1, self.max_attempts + 1):
            remaining = deadline - self._now()
            if remaining <= 0:
                raise RetryExhausted("deadline", attempt - 1) from last_transient
            timeout = min(self.max_attempt_seconds, remaining)
            try:
                return operation(timeout)
            except PermanentFailure:
                raise
            except TransientFailure as error:
                last_transient = error
                if not safety.permits_repeat():
                    raise RetryNotSafe("retry_not_safe") from error
                if attempt == self.max_attempts:
                    raise RetryExhausted("attempts", attempt) from error
                delay = self.backoffs[attempt - 1]
                if self._now() + delay > deadline:
                    raise RetryExhausted("deadline", attempt) from error
                if delay:
                    self._clock.advance(delay)
                self.used_backoffs.append(delay)

        raise AssertionError("the bounded attempt loop must return or raise")


def main() -> None:
    happy_clock = FakeClock()
    happy_dependency = ScriptedDependency(
        happy_clock,
        [
            Outcome(0.02, error=TransientFailure("temporary")),
            Outcome(0.01, value="temperature=21"),
        ],
    )
    happy_policy = RetryPolicy(happy_clock)
    result = happy_policy.run(happy_dependency, RetrySafety(side_effect_free=True))
    print(
        f"happy result={result} calls={happy_dependency.calls} "
        f"backoffs={happy_policy.used_backoffs} elapsed={happy_clock():.2f}"
    )

    unsafe_clock = FakeClock()
    unsafe_dependency = ScriptedDependency(
        unsafe_clock,
        [Outcome[str](0.01, error=TransientFailure("write_outcome_unknown"))],
    )
    try:
        RetryPolicy(unsafe_clock).run(
            unsafe_dependency,
            RetrySafety(idempotency_key="job-7", deduplication_enforced=False),
        )
    except RetryNotSafe as error:
        print(f"boundary code={error} calls={unsafe_dependency.calls}")

    deadline_clock = FakeClock()
    deadline_dependency = ScriptedDependency(
        deadline_clock,
        [Outcome[str](0.08, error=TransientFailure("temporary"))],
    )
    deadline_policy = RetryPolicy(deadline_clock, total_budget_seconds=0.12)
    try:
        deadline_policy.run(deadline_dependency, RetrySafety(side_effect_free=True))
    except RetryExhausted as error:
        print(
            f"recoverable code={error} calls={deadline_dependency.calls} "
            f"backoffs={deadline_policy.used_backoffs}"
        )

    recovery_dependency = ScriptedDependency(
        deadline_clock, [Outcome(0.01, value="ok")]
    )
    recovery = RetryPolicy(deadline_clock).run(
        recovery_dependency, RetrySafety(side_effect_free=True)
    )
    print(f"recovery result={recovery} calls={recovery_dependency.calls}")

    try:
        RetryPolicy(FakeClock(), max_attempts=True)
    except ValueError as error:
        print(f"config_boundary code={error}")

    try:
        Outcome(float("inf"))
    except ValueError as error:
        print(f"input_recovery code={error} later_result={recovery}")


if __name__ == "__main__":
    main()
