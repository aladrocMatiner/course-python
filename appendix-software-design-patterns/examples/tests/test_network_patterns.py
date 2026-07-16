from __future__ import annotations

import ast
import asyncio
import subprocess
import sys
import unittest
from pathlib import Path


EXAMPLES = Path(__file__).parents[1]
sys.path.insert(0, str(EXAMPLES))

from patterns.resilience import (  # noqa: E402
    CircuitBreaker,
    CircuitOpen,
    CircuitState,
    COOLDOWN_SECONDS,
    DeduplicatingDependency,
    FAILURE_THRESHOLD,
    FakeClock,
    FakeSleeper,
    MAX_ATTEMPTS,
    MAX_ATTEMPT_TIMEOUT_SECONDS,
    PUBLISHED_BACKOFF_SECONDS,
    PermanentDependencyError,
    RetryExhausted,
    RetryPolicy,
    RetrySafety,
    TOTAL_DEADLINE_SECONDS,
    TransientDependencyError,
    ValidationError,
)


def load_capacity_api() -> tuple[object, ...]:
    """Import Capacity only when its later checkpoint is selected."""

    from patterns.capacity import (
        EXECUTION_LIMIT,
        MAX_ADMISSION_TIMEOUT_SECONDS,
        WAITING_LIMIT,
        BulkheadSet,
        Overloaded,
    )

    return (
        EXECUTION_LIMIT,
        MAX_ADMISSION_TIMEOUT_SECONDS,
        WAITING_LIMIT,
        BulkheadSet,
        Overloaded,
    )


def load_pubsub_api() -> tuple[object, ...]:
    """Import optional Pub/Sub only when its maintained extension is selected."""

    from patterns.pubsub import (
        MAX_QUEUED_PER_SUBSCRIBER,
        MAX_SUBSCRIBERS,
        NoPendingEvent,
        PubSub,
        ResourceLimit,
        UnknownSubscriber,
    )

    return (
        MAX_QUEUED_PER_SUBSCRIBER,
        MAX_SUBSCRIBERS,
        NoPendingEvent,
        PubSub,
        ResourceLimit,
        UnknownSubscriber,
    )


async def wait_until(predicate: object, *, turns: int = 50) -> None:
    """Yield deterministically until an in-memory state transition is visible."""

    for _ in range(turns):
        if predicate():  # type: ignore[operator]
            return
        await asyncio.sleep(0)
    raise AssertionError("expected state transition did not occur")


class NetworkAsyncTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        await asyncio.sleep(0)
        current = asyncio.current_task()
        leaked = [
            task
            for task in asyncio.all_tasks()
            if task is not current
            and not task.done()
            and task.get_name().startswith("patterns-")
        ]
        self.assertEqual(leaked, [], "an Appendix C policy task survived its test")


class CapacityNetworkTestCase(NetworkAsyncTestCase):
    """Load Capacity only for the checkpoint that owns it."""

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        (
            self.EXECUTION_LIMIT,
            self.MAX_ADMISSION_TIMEOUT_SECONDS,
            self.WAITING_LIMIT,
            self.BulkheadSet,
            self.Overloaded,
        ) = load_capacity_api()


class RetryPolicyTests(NetworkAsyncTestCase):
    def make_policy(
        self, *, auto_advance: bool = True
    ) -> tuple[FakeClock, FakeSleeper, RetryPolicy]:
        clock = FakeClock()
        sleeper = FakeSleeper(clock, auto_advance=auto_advance)
        return clock, sleeper, RetryPolicy(clock, sleeper)

    async def test_published_retry_defaults_use_named_bounds(self) -> None:
        _, _, policy = self.make_policy()

        self.assertEqual(MAX_ATTEMPTS, 3)
        self.assertEqual(MAX_ATTEMPT_TIMEOUT_SECONDS, 0.1)
        self.assertEqual(TOTAL_DEADLINE_SECONDS, 0.5)
        self.assertEqual(PUBLISHED_BACKOFF_SECONDS, (0.05, 0.1))
        self.assertEqual(policy.max_attempts, MAX_ATTEMPTS)
        self.assertEqual(policy.attempt_timeout, MAX_ATTEMPT_TIMEOUT_SECONDS)
        self.assertEqual(policy.total_deadline, TOTAL_DEADLINE_SECONDS)

    async def test_retry_configuration_cannot_exceed_published_maxima(self) -> None:
        clock = FakeClock()
        sleeper = FakeSleeper(clock)
        invalid_options = (
            {"max_attempts": 4, "backoffs": (0.05, 0.1, 0.1)},
            {"attempt_timeout": 0.101},
            {"total_deadline": 0.501},
            {"max_attempts": 2, "backoffs": (0.01,)},
            {"backoffs": (0.051, 0.1)},
            {"backoffs": (0.05, 0.1, 0.1)},
        )

        for options in invalid_options:
            with self.subTest(options=options), self.assertRaises(ValueError):
                RetryPolicy(clock, sleeper, **options)  # type: ignore[arg-type]

        smaller = RetryPolicy(
            clock,
            sleeper,
            max_attempts=2,
            attempt_timeout=0.05,
            total_deadline=0.2,
            backoffs=(0.05,),
        )
        self.assertEqual(smaller.max_attempts, 2)

    async def test_retry_safe_transient_operation_recovers_on_third_attempt(self) -> None:
        clock, sleeper, policy = self.make_policy()
        outcomes: list[object] = [
            TransientDependencyError(),
            TransientDependencyError(),
            "accepted",
        ]
        calls = 0

        async def operation() -> str:
            nonlocal calls
            calls += 1
            outcome = outcomes.pop(0)
            if isinstance(outcome, BaseException):
                raise outcome
            return str(outcome)

        result = await policy.execute(operation, RetrySafety.read_only())

        self.assertEqual(result, "accepted")
        self.assertEqual(calls, 3)
        self.assertEqual(sleeper.completed, [0.050, 0.100])
        self.assertAlmostEqual(clock(), 0.150)
        self.assertEqual(policy.owned_task_count, 0)

    async def test_dependency_enforced_key_records_one_effect(self) -> None:
        _, _, policy = self.make_policy()
        dependency = DeduplicatingDependency(
            enforces_deduplication=True,
            lost_responses=2,
        )
        key = "job-key-1"
        safety = RetrySafety.deduplicated(
            key, enforced=dependency.enforces_deduplication
        )

        result = await policy.execute(
            lambda: dependency.perform(key, "report"),
            safety,
        )

        self.assertEqual(result, "stored:report")
        self.assertEqual(dependency.calls, 3)
        self.assertEqual(dependency.effect_count, 1)

    async def test_key_without_dependency_enforcement_is_not_retry_safe(self) -> None:
        _, _, policy = self.make_policy()
        dependency = DeduplicatingDependency(
            enforces_deduplication=False,
            lost_responses=2,
        )
        safety = RetrySafety.deduplicated(
            "job-key-2", enforced=dependency.enforces_deduplication
        )

        with self.assertRaises(TransientDependencyError) as caught:
            await policy.execute(
                lambda: dependency.perform("job-key-2", "report"),
                safety,
            )

        self.assertEqual(caught.exception.code, "response_lost")
        self.assertFalse(safety.retry_safe)
        self.assertEqual(dependency.calls, 1)
        self.assertEqual(dependency.effect_count, 1)

    async def test_permanent_failure_stops_after_one_call(self) -> None:
        _, sleeper, policy = self.make_policy()
        calls = 0

        async def operation() -> None:
            nonlocal calls
            calls += 1
            raise PermanentDependencyError()

        with self.assertRaises(PermanentDependencyError):
            await policy.execute(operation, RetrySafety.read_only())

        self.assertEqual(calls, 1)
        self.assertEqual(sleeper.completed, [])

    async def test_backoff_starts_only_when_its_full_duration_fits(self) -> None:
        clock, sleeper, policy = self.make_policy()
        deadline = policy.new_deadline()
        clock.advance(0.460)
        calls = 0

        async def operation() -> None:
            nonlocal calls
            calls += 1
            raise TransientDependencyError("late_transient")

        with self.assertRaises(RetryExhausted) as caught:
            await policy.execute(
                operation,
                RetrySafety.read_only(),
                deadline=deadline,
            )

        self.assertEqual(calls, 1)
        self.assertEqual(sleeper.completed, [])
        self.assertEqual(caught.exception.__cause__.code, "late_transient")
        self.assertLessEqual(clock(), 0.500)

    async def test_exactly_fitting_backoff_completes_without_a_late_call(self) -> None:
        clock, sleeper, policy = self.make_policy()
        deadline = policy.new_deadline()
        clock.advance(0.450)
        calls = 0

        async def operation() -> None:
            nonlocal calls
            calls += 1
            raise TransientDependencyError("boundary_transient")

        with self.assertRaises(RetryExhausted) as caught:
            await policy.execute(
                operation,
                RetrySafety.read_only(),
                deadline=deadline,
            )

        self.assertEqual(calls, 1)
        self.assertEqual(sleeper.completed, [0.050])
        self.assertAlmostEqual(clock(), TOTAL_DEADLINE_SECONDS)
        self.assertEqual(caught.exception.__cause__.code, "boundary_transient")

    async def test_overtime_success_and_error_map_to_attempt_timeout(self) -> None:
        for outcome in ("success", "error"):
            with self.subTest(outcome=outcome):
                clock, sleeper, policy = self.make_policy()
                calls = 0

                async def overtime_operation() -> str:
                    nonlocal calls
                    calls += 1
                    clock.advance(MAX_ATTEMPT_TIMEOUT_SECONDS + 0.001)
                    if outcome == "error":
                        raise PermanentDependencyError()
                    return "too-late"

                with self.assertRaises(TransientDependencyError) as caught:
                    await policy.execute(overtime_operation, RetrySafety())

                self.assertEqual(caught.exception.code, "attempt_timeout")
                self.assertEqual(calls, 1)
                self.assertEqual(sleeper.completed, [])
                self.assertEqual(policy.owned_task_count, 0)

    async def test_stalled_attempts_are_cancelled_awaited_and_exhausted(self) -> None:
        clock, _, policy = self.make_policy()
        cleanups = 0

        async def operation() -> None:
            nonlocal cleanups
            try:
                await asyncio.Future()
            finally:
                cleanups += 1

        with self.assertRaises(RetryExhausted) as caught:
            await policy.execute(operation, RetrySafety.read_only())

        self.assertEqual(cleanups, 3)
        self.assertEqual(caught.exception.__cause__.code, "attempt_timeout")
        self.assertLessEqual(clock(), 0.500)
        self.assertEqual(policy.owned_task_count, 0)

    async def test_caller_cancellation_propagates_and_cleans_attempt(self) -> None:
        _, sleeper, policy = self.make_policy(auto_advance=False)
        started = asyncio.Event()
        cleaned = asyncio.Event()

        async def operation() -> None:
            started.set()
            try:
                await asyncio.Future()
            finally:
                cleaned.set()

        task = asyncio.create_task(
            policy.execute(operation, RetrySafety.read_only()),
            name="test-caller-operation",
        )
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task

        self.assertTrue(cleaned.is_set())
        self.assertEqual(sleeper.pending_count, 0)
        self.assertEqual(policy.owned_task_count, 0)


class CircuitBreakerTests(NetworkAsyncTestCase):
    def make_breaker(
        self, *, auto_advance: bool = True
    ) -> tuple[FakeClock, FakeSleeper, RetryPolicy, CircuitBreaker]:
        clock = FakeClock()
        sleeper = FakeSleeper(clock, auto_advance=auto_advance)
        retry = RetryPolicy(clock, sleeper)
        return clock, sleeper, retry, CircuitBreaker(retry, clock)

    async def test_three_exhausted_operations_open_after_nine_calls(self) -> None:
        _, _, retry, breaker = self.make_breaker()
        calls = 0

        async def unavailable() -> None:
            nonlocal calls
            calls += 1
            raise TransientDependencyError()

        for _ in range(3):
            with self.assertRaises(RetryExhausted):
                await breaker.execute(unavailable, RetrySafety.read_only())

        self.assertEqual(calls, 9)
        self.assertEqual(breaker.state, CircuitState.OPEN)
        self.assertEqual(breaker.failure_count, 3)
        with self.assertRaises(CircuitOpen) as caught:
            await breaker.execute(unavailable, RetrySafety.read_only())
        self.assertEqual(caught.exception.code, "circuit_open")
        self.assertEqual(calls, 9)
        self.assertEqual(retry.owned_task_count, 0)

    async def test_positive_health_resets_consecutive_negatives(self) -> None:
        _, _, _, breaker = self.make_breaker()

        async def unavailable() -> None:
            raise TransientDependencyError()

        async def healthy() -> str:
            return "ok"

        for _ in range(2):
            with self.assertRaises(RetryExhausted):
                await breaker.execute(unavailable, RetrySafety.read_only())
        self.assertEqual(await breaker.execute(healthy, RetrySafety.read_only()), "ok")
        for _ in range(2):
            with self.assertRaises(RetryExhausted):
                await breaker.execute(unavailable, RetrySafety.read_only())

        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.failure_count, 2)

    async def test_responsive_permanent_failure_resets_but_propagates(self) -> None:
        _, _, _, breaker = self.make_breaker()

        async def unavailable() -> None:
            raise TransientDependencyError()

        for _ in range(2):
            with self.assertRaises(RetryExhausted):
                await breaker.execute(unavailable, RetrySafety.read_only())

        async def permanent() -> None:
            raise PermanentDependencyError()

        with self.assertRaises(PermanentDependencyError):
            await breaker.execute(permanent, RetrySafety.read_only())
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)

    async def test_unsafe_raw_transients_open_after_three_calls(self) -> None:
        _, _, _, breaker = self.make_breaker()
        calls = 0

        async def unavailable_write() -> None:
            nonlocal calls
            calls += 1
            raise TransientDependencyError()

        for _ in range(3):
            with self.assertRaises(TransientDependencyError):
                await breaker.execute(unavailable_write, RetrySafety())

        self.assertEqual(calls, 3)
        self.assertEqual(breaker.state, CircuitState.OPEN)

    async def test_breaker_configuration_is_exact_not_tunable(self) -> None:
        clock = FakeClock()
        retry = RetryPolicy(clock, FakeSleeper(clock))

        self.assertEqual(FAILURE_THRESHOLD, 3)
        self.assertEqual(COOLDOWN_SECONDS, 1.0)
        with self.assertRaises(ValueError):
            CircuitBreaker(retry, clock, failure_threshold=2)
        with self.assertRaises(ValueError):
            CircuitBreaker(retry, clock, failure_threshold=4)
        with self.assertRaises(ValueError):
            CircuitBreaker(retry, clock, cooldown=0.5)
        with self.assertRaises(ValueError):
            CircuitBreaker(retry, clock, cooldown=2.0)

    async def test_validation_is_neutral_and_makes_no_dependency_call(self) -> None:
        _, _, _, breaker = self.make_breaker()
        dependency_calls = 0

        async def unavailable() -> None:
            raise TransientDependencyError()

        with self.assertRaises(TransientDependencyError):
            await breaker.execute(unavailable, RetrySafety())
        self.assertEqual(breaker.failure_count, 1)

        def validate_request() -> None:
            raise ValidationError("missing dependency request")

        async def dependency() -> None:
            nonlocal dependency_calls
            dependency_calls += 1

        with self.assertRaises(ValidationError):
            await breaker.execute(
                dependency,
                RetrySafety.read_only(),
                validate=validate_request,
            )

        self.assertEqual(dependency_calls, 0)
        self.assertEqual(breaker.failure_count, 1)
        self.assertEqual(breaker.state, CircuitState.CLOSED)

        for _ in range(2):
            with self.assertRaises(TransientDependencyError):
                await breaker.execute(unavailable, RetrySafety())
        self.assertEqual(breaker.state, CircuitState.OPEN)

        with self.assertRaises(ValidationError):
            await breaker.execute(
                dependency,
                RetrySafety.read_only(),
                validate=validate_request,
            )
        self.assertEqual(dependency_calls, 0)
        self.assertEqual(breaker.failure_count, FAILURE_THRESHOLD)
        self.assertEqual(breaker.state, CircuitState.OPEN)

    async def test_caller_cancellation_is_neutral_and_cleans_owned_attempt(self) -> None:
        _, sleeper, retry, breaker = self.make_breaker(auto_advance=False)

        async def unavailable() -> None:
            raise TransientDependencyError()

        with self.assertRaises(TransientDependencyError):
            await breaker.execute(unavailable, RetrySafety())
        self.assertEqual(breaker.failure_count, 1)

        started = asyncio.Event()
        cleaned = asyncio.Event()

        async def pending_dependency() -> None:
            started.set()
            try:
                await asyncio.Future()
            finally:
                cleaned.set()

        operation = asyncio.create_task(
            breaker.execute(pending_dependency, RetrySafety.read_only()),
            name="test-cancelled-breaker-operation",
        )
        await started.wait()
        operation.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await operation

        self.assertTrue(cleaned.is_set())
        self.assertEqual(breaker.failure_count, 1)
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(sleeper.pending_count, 0)
        self.assertEqual(retry.owned_task_count, 0)

    async def test_cancellation_after_transient_is_one_negative_observation(self) -> None:
        _, sleeper, retry, breaker = self.make_breaker(auto_advance=False)
        calls = 0

        async def unavailable() -> None:
            nonlocal calls
            calls += 1
            raise TransientDependencyError("observed_before_cancel")

        for logical_operation in range(1, FAILURE_THRESHOLD + 1):
            operation = asyncio.create_task(
                breaker.execute(unavailable, RetrySafety.read_only()),
                name=f"test-cancel-after-transient-{logical_operation}",
            )
            await wait_until(
                lambda: calls == logical_operation
                and sleeper.pending_count == 1
                and sleeper.requested[-1:] == [0.05]
            )
            operation.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await operation

            self.assertEqual(breaker.failure_count, logical_operation)
            self.assertEqual(sleeper.pending_count, 0)
            self.assertEqual(retry.owned_task_count, 0)

        self.assertEqual(calls, FAILURE_THRESHOLD)
        self.assertEqual(breaker.state, CircuitState.OPEN)

    async def test_half_open_probe_is_exclusive_and_success_closes(self) -> None:
        clock, _, _, breaker = self.make_breaker(auto_advance=False)

        async def unavailable() -> None:
            raise TransientDependencyError()

        for _ in range(3):
            with self.assertRaises(TransientDependencyError):
                await breaker.execute(unavailable, RetrySafety())
        clock.advance(1.0)

        started = asyncio.Event()
        finish = asyncio.Event()

        async def probe() -> str:
            started.set()
            await finish.wait()
            return "healthy"

        probe_task = asyncio.create_task(
            breaker.execute(probe, RetrySafety()), name="test-half-open-probe"
        )
        await started.wait()
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)
        with self.assertRaises(CircuitOpen):
            await breaker.execute(probe, RetrySafety())
        finish.set()
        self.assertEqual(await probe_task, "healthy")
        self.assertEqual(breaker.state, CircuitState.CLOSED)

    async def test_half_open_transient_reopens_with_fresh_cooldown(self) -> None:
        clock, _, _, breaker = self.make_breaker()
        calls = 0

        async def unavailable() -> None:
            nonlocal calls
            calls += 1
            raise TransientDependencyError("probe_transient")

        for _ in range(FAILURE_THRESHOLD):
            with self.assertRaises(TransientDependencyError):
                await breaker.execute(unavailable, RetrySafety())
        self.assertEqual(calls, FAILURE_THRESHOLD)
        clock.advance(COOLDOWN_SECONDS)

        with self.assertRaises(TransientDependencyError) as caught:
            await breaker.execute(unavailable, RetrySafety.read_only())

        self.assertEqual(caught.exception.code, "probe_transient")
        self.assertEqual(calls, FAILURE_THRESHOLD + 1)
        self.assertEqual(breaker.state, CircuitState.OPEN)
        self.assertAlmostEqual(
            breaker.next_probe_at,
            clock() + COOLDOWN_SECONDS,
        )

    async def test_half_open_timeout_reopens_and_cleans_probe(self) -> None:
        clock, sleeper, retry, breaker = self.make_breaker()

        async def unavailable() -> None:
            raise TransientDependencyError()

        for _ in range(FAILURE_THRESHOLD):
            with self.assertRaises(TransientDependencyError):
                await breaker.execute(unavailable, RetrySafety())
        clock.advance(COOLDOWN_SECONDS)
        cleaned = asyncio.Event()

        async def stalled_probe() -> None:
            try:
                await asyncio.Future()
            finally:
                cleaned.set()

        with self.assertRaises(TransientDependencyError) as caught:
            await breaker.execute(stalled_probe, RetrySafety.read_only())

        self.assertEqual(caught.exception.code, "attempt_timeout")
        self.assertTrue(cleaned.is_set())
        self.assertEqual(breaker.state, CircuitState.OPEN)
        self.assertAlmostEqual(
            breaker.next_probe_at,
            clock() + COOLDOWN_SECONDS,
        )
        self.assertEqual(sleeper.pending_count, 0)
        self.assertEqual(retry.owned_task_count, 0)

    async def test_half_open_permanent_response_closes_and_propagates(self) -> None:
        clock, _, _, breaker = self.make_breaker()
        probe_calls = 0

        async def unavailable() -> None:
            raise TransientDependencyError()

        for _ in range(FAILURE_THRESHOLD):
            with self.assertRaises(TransientDependencyError):
                await breaker.execute(unavailable, RetrySafety())
        clock.advance(COOLDOWN_SECONDS)

        async def permanent_probe() -> None:
            nonlocal probe_calls
            probe_calls += 1
            raise PermanentDependencyError("probe_permanent")

        with self.assertRaises(PermanentDependencyError) as caught:
            await breaker.execute(permanent_probe, RetrySafety.read_only())

        self.assertEqual(caught.exception.code, "probe_permanent")
        self.assertEqual(probe_calls, 1)
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)

    async def test_cancelled_probe_releases_lease_without_new_cooldown(self) -> None:
        clock, sleeper, _, breaker = self.make_breaker(auto_advance=False)

        async def unavailable() -> None:
            raise TransientDependencyError()

        for _ in range(3):
            with self.assertRaises(TransientDependencyError):
                await breaker.execute(unavailable, RetrySafety())
        clock.advance(1.0)
        original_probe_time = breaker.next_probe_at

        started = asyncio.Event()

        async def probe() -> None:
            started.set()
            await asyncio.Future()

        probe_task = asyncio.create_task(
            breaker.execute(probe, RetrySafety()), name="test-cancelled-probe"
        )
        await started.wait()
        probe_task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await probe_task

        self.assertEqual(breaker.state, CircuitState.OPEN)
        self.assertEqual(breaker.next_probe_at, original_probe_time)
        self.assertLessEqual(breaker.next_probe_at, clock())
        self.assertEqual(sleeper.pending_count, 0)


class BulkheadTests(CapacityNetworkTestCase):
    async def test_published_bulkhead_limits_are_fixed(self) -> None:
        clock = FakeClock()
        remote = self.BulkheadSet(clock, FakeSleeper(clock))["remote"]

        self.assertEqual(self.EXECUTION_LIMIT, 1)
        self.assertEqual(self.WAITING_LIMIT, 1)
        self.assertEqual(self.MAX_ADMISSION_TIMEOUT_SECONDS, 0.05)
        self.assertEqual(remote.execution_limit, self.EXECUTION_LIMIT)
        self.assertEqual(remote.waiting_limit, self.WAITING_LIMIT)
        self.assertEqual(
            remote.admission_timeout,
            self.MAX_ADMISSION_TIMEOUT_SECONDS,
        )
        with self.assertRaises(ValueError):
            self.BulkheadSet(clock, FakeSleeper(clock), admission_timeout=0.051)

    async def test_remote_saturation_does_not_consume_local_capacity(self) -> None:
        clock = FakeClock()
        sleeper = FakeSleeper(clock, auto_advance=False)
        bulkheads = self.BulkheadSet(clock, sleeper)
        remote = bulkheads["remote"]
        local = bulkheads["local"]
        deadline = clock() + 0.500

        executing = await remote.acquire(deadline=deadline)
        queued_task = asyncio.create_task(
            remote.acquire(deadline=deadline), name="test-remote-waiter"
        )
        await wait_until(lambda: remote.waiting)

        with self.assertRaises(self.Overloaded) as caught:
            await remote.acquire(deadline=deadline)
        self.assertEqual(caught.exception.code, "overloaded")

        local_lease = await local.acquire(deadline=deadline)
        self.assertTrue(local.executing)
        local_lease.release()

        executing.release()
        queued = await queued_task
        self.assertTrue(remote.executing)
        self.assertFalse(remote.waiting)
        queued.release()
        self.assertFalse(remote.executing)
        self.assertEqual(sleeper.pending_count, 0)
        self.assertEqual(bulkheads.owned_task_count, 0)

    async def test_waiter_expiry_recovers_capacity(self) -> None:
        clock = FakeClock()
        sleeper = FakeSleeper(clock, auto_advance=False)
        remote = self.BulkheadSet(clock, sleeper)["remote"]
        deadline = clock() + 0.500
        executing = await remote.acquire(deadline=deadline)
        queued_task = asyncio.create_task(
            remote.acquire(deadline=deadline), name="test-expiring-waiter"
        )
        await wait_until(lambda: remote.waiting and sleeper.pending_count == 1)
        sleeper.advance(0.050)

        with self.assertRaises(self.Overloaded) as caught:
            await queued_task
        self.assertEqual(caught.exception.code, "admission_timeout")
        self.assertFalse(remote.waiting)

        executing.release()
        later = await remote.acquire(deadline=clock() + 0.500)
        later.release()
        self.assertFalse(remote.executing)

    async def test_expiry_wins_over_same_turn_promotion(self) -> None:
        clock = FakeClock()
        sleeper = FakeSleeper(clock, auto_advance=False)
        remote = self.BulkheadSet(clock, sleeper)["remote"]
        deadline = clock() + TOTAL_DEADLINE_SECONDS
        executing = await remote.acquire(deadline=deadline)
        queued_task = asyncio.create_task(
            remote.acquire(deadline=deadline), name="test-expiry-promotion-race"
        )
        await wait_until(lambda: remote.waiting and sleeper.pending_count == 1)

        sleeper.advance(self.MAX_ADMISSION_TIMEOUT_SECONDS)
        executing.release()

        with self.assertRaises(self.Overloaded) as caught:
            await queued_task
        self.assertEqual(caught.exception.code, "admission_timeout")
        self.assertFalse(remote.executing)
        self.assertFalse(remote.waiting)
        self.assertEqual(sleeper.pending_count, 0)

        recovered = await remote.acquire(deadline=clock() + TOTAL_DEADLINE_SECONDS)
        recovered.release()
        self.assertFalse(remote.executing)

    async def test_lease_release_is_idempotent_after_waiter_promotion(self) -> None:
        clock = FakeClock()
        sleeper = FakeSleeper(clock, auto_advance=False)
        remote = self.BulkheadSet(clock, sleeper)["remote"]
        deadline = clock() + TOTAL_DEADLINE_SECONDS
        executing = await remote.acquire(deadline=deadline)
        queued_task = asyncio.create_task(
            remote.acquire(deadline=deadline), name="test-idempotent-release-waiter"
        )
        await wait_until(lambda: remote.waiting)

        executing.release()
        executing.release()
        queued = await queued_task

        self.assertTrue(remote.executing)
        self.assertFalse(remote.waiting)
        queued.release()
        self.assertFalse(remote.executing)
        self.assertEqual(sleeper.pending_count, 0)

    async def test_cancelled_waiter_is_removed_exactly_once(self) -> None:
        clock = FakeClock()
        sleeper = FakeSleeper(clock, auto_advance=False)
        remote = self.BulkheadSet(clock, sleeper)["remote"]
        executing = await remote.acquire(deadline=clock() + 0.500)
        queued_task = asyncio.create_task(
            remote.acquire(deadline=clock() + 0.500), name="test-cancelled-waiter"
        )
        await wait_until(lambda: remote.waiting)
        queued_task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await queued_task

        self.assertFalse(remote.waiting)
        self.assertEqual(sleeper.pending_count, 0)
        executing.release()
        self.assertFalse(remote.executing)

    async def test_cancelled_execution_releases_lease(self) -> None:
        clock = FakeClock()
        sleeper = FakeSleeper(clock, auto_advance=False)
        remote = self.BulkheadSet(clock, sleeper)["remote"]
        started = asyncio.Event()
        cleaned = asyncio.Event()

        async def operation() -> None:
            started.set()
            try:
                await asyncio.Future()
            finally:
                cleaned.set()

        task = asyncio.create_task(
            remote.run(operation, deadline=clock() + 0.500),
            name="test-cancelled-execution",
        )
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertTrue(cleaned.is_set())
        self.assertFalse(remote.executing)

    async def test_admission_uses_lesser_remaining_deadline(self) -> None:
        clock = FakeClock()
        sleeper = FakeSleeper(clock)
        remote = self.BulkheadSet(clock, sleeper)["remote"]
        executing = await remote.acquire(deadline=clock() + 0.500)

        with self.assertRaises(self.Overloaded) as caught:
            await remote.acquire(deadline=clock() + 0.020)

        self.assertEqual(caught.exception.code, "admission_timeout")
        self.assertAlmostEqual(clock(), 0.020)
        executing.release()


class CapacityCompositionTests(CapacityNetworkTestCase):
    async def test_capacity_lease_is_released_before_retry_backoff(self) -> None:
        clock = FakeClock()
        base_sleeper = FakeSleeper(clock)
        bulkhead = self.BulkheadSet(clock, base_sleeper)["remote"]
        backoff_observations: list[bool] = []
        competing_calls = 0

        async def competing_operation() -> None:
            nonlocal competing_calls
            competing_calls += 1

        async def observed_sleep(seconds: float) -> None:
            if seconds == 0.050:
                backoff_observations.append(bulkhead.executing)
                await bulkhead.run(competing_operation, deadline=deadline)
            await base_sleeper(seconds)

        retry = RetryPolicy(clock, observed_sleep)
        deadline = retry.new_deadline()
        calls = 0

        async def dependency() -> str:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise TransientDependencyError()
            return "ok"

        result = await retry.execute(
            dependency,
            RetrySafety.read_only(),
            deadline=deadline,
            acquire_attempt_lease=lambda attempt_deadline: bulkhead.acquire(
                deadline=attempt_deadline
            ),
        )

        self.assertEqual(result, "ok")
        self.assertEqual(backoff_observations, [False])
        self.assertEqual(competing_calls, 1)
        self.assertFalse(bulkhead.executing)

    async def test_first_admission_timeout_is_local_and_neutral(self) -> None:
        clock = FakeClock()
        retry_sleeper = FakeSleeper(clock, auto_advance=False)
        capacity_sleeper = FakeSleeper(clock)
        retry = RetryPolicy(clock, retry_sleeper)
        breaker = CircuitBreaker(retry, clock)
        remote = self.BulkheadSet(clock, capacity_sleeper)["remote"]
        deadline = retry.new_deadline()
        blocker = await remote.acquire(deadline=deadline)
        dependency_calls = 0

        async def dependency() -> None:
            nonlocal dependency_calls
            dependency_calls += 1

        try:
            with self.assertRaises(self.Overloaded) as caught:
                await breaker.execute(
                    dependency,
                    RetrySafety.read_only(),
                    deadline=deadline,
                    acquire_attempt_lease=lambda attempt_deadline: remote.acquire(
                        deadline=attempt_deadline
                    ),
                )
        finally:
            blocker.release()

        self.assertEqual(caught.exception.code, "admission_timeout")
        self.assertEqual(dependency_calls, 0)
        self.assertEqual(breaker.failure_count, 0)
        self.assertEqual(breaker.state, CircuitState.CLOSED)

    async def test_integrated_admission_consumes_last_twenty_ms_of_deadline(self) -> None:
        clock = FakeClock()
        retry_sleeper = FakeSleeper(clock)
        capacity_sleeper = FakeSleeper(clock)
        retry = RetryPolicy(clock, retry_sleeper)
        breaker = CircuitBreaker(retry, clock)
        remote = self.BulkheadSet(clock, capacity_sleeper)["remote"]
        deadline = retry.new_deadline()
        clock.advance(0.480)
        blocker = await remote.acquire(deadline=deadline)
        dependency_calls = 0

        async def dependency() -> None:
            nonlocal dependency_calls
            dependency_calls += 1

        try:
            with self.assertRaises(self.Overloaded) as caught:
                await breaker.execute(
                    dependency,
                    RetrySafety.read_only(),
                    deadline=deadline,
                    acquire_attempt_lease=lambda attempt_deadline: remote.acquire(
                        deadline=attempt_deadline
                    ),
                )
        finally:
            blocker.release()

        self.assertEqual(caught.exception.code, "admission_timeout")
        self.assertEqual(dependency_calls, 0)
        self.assertAlmostEqual(clock(), TOTAL_DEADLINE_SECONDS)
        self.assertEqual(retry_sleeper.requested, [])
        self.assertEqual(retry.owned_task_count, 0)
        self.assertEqual(breaker.failure_count, 0)
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertFalse(remote.executing)
        self.assertFalse(remote.waiting)
        self.assertEqual(capacity_sleeper.pending_count, 0)

    async def test_admission_timeout_after_transient_preserves_cause_once(self) -> None:
        clock = FakeClock()
        retry_sleeper = FakeSleeper(clock, auto_advance=False)
        capacity_sleeper = FakeSleeper(clock)
        retry = RetryPolicy(clock, retry_sleeper)
        breaker = CircuitBreaker(retry, clock)
        remote = self.BulkheadSet(clock, capacity_sleeper)["remote"]
        deadline = retry.new_deadline()
        dependency_calls = 0
        blocker = None

        async def dependency() -> None:
            nonlocal dependency_calls
            dependency_calls += 1
            raise TransientDependencyError("first_transient")

        operation = asyncio.create_task(
            breaker.execute(
                dependency,
                RetrySafety.read_only(),
                deadline=deadline,
                acquire_attempt_lease=lambda attempt_deadline: remote.acquire(
                    deadline=attempt_deadline
                ),
            ),
            name="test-prior-transient-operation",
        )
        await wait_until(
            lambda: dependency_calls == 1
            and not remote.executing
            and retry_sleeper.pending_count == 1
            and retry_sleeper.requested[-1:] == [0.050]
        )
        blocker = await remote.acquire(deadline=deadline)
        retry_sleeper.advance(0.050)
        try:
            with self.assertRaises(RetryExhausted) as caught:
                await operation
        finally:
            blocker.release()

        self.assertEqual(caught.exception.__cause__.code, "first_transient")
        self.assertEqual(dependency_calls, 1)
        self.assertEqual(breaker.failure_count, 1)
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertFalse(remote.waiting)
        self.assertEqual(retry.owned_task_count, 0)

    async def test_cancel_after_transient_during_admission_is_one_negative(self) -> None:
        clock = FakeClock()
        retry_sleeper = FakeSleeper(clock, auto_advance=False)
        capacity_sleeper = FakeSleeper(clock, auto_advance=False)
        retry = RetryPolicy(clock, retry_sleeper)
        breaker = CircuitBreaker(retry, clock)
        remote = self.BulkheadSet(clock, capacity_sleeper)["remote"]
        deadline = retry.new_deadline()
        dependency_calls = 0

        async def dependency() -> None:
            nonlocal dependency_calls
            dependency_calls += 1
            raise TransientDependencyError("before_admission_cancel")

        operation = asyncio.create_task(
            breaker.execute(
                dependency,
                RetrySafety.read_only(),
                deadline=deadline,
                acquire_attempt_lease=lambda attempt_deadline: remote.acquire(
                    deadline=attempt_deadline
                ),
            ),
            name="test-cancel-during-retry-admission",
        )
        await wait_until(
            lambda: dependency_calls == 1
            and not remote.executing
            and retry_sleeper.pending_count == 1
            and retry_sleeper.requested[-1:] == [0.05]
        )
        blocker = await remote.acquire(deadline=deadline)
        retry_sleeper.advance(0.05)
        await wait_until(
            lambda: remote.waiting and capacity_sleeper.pending_count == 1
        )

        operation.cancel()
        try:
            with self.assertRaises(asyncio.CancelledError):
                await operation
        finally:
            blocker.release()

        self.assertEqual(dependency_calls, 1)
        self.assertEqual(breaker.failure_count, 1)
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertFalse(remote.executing)
        self.assertFalse(remote.waiting)
        self.assertEqual(retry_sleeper.pending_count, 0)
        self.assertEqual(capacity_sleeper.pending_count, 0)
        self.assertEqual(retry.owned_task_count, 0)

    async def test_open_circuit_fails_before_capacity(self) -> None:
        clock = FakeClock()
        sleeper = FakeSleeper(clock)
        retry = RetryPolicy(clock, sleeper)
        breaker = CircuitBreaker(retry, clock)
        remote = self.BulkheadSet(clock, sleeper)["remote"]
        dependency_calls = 0

        async def unavailable() -> None:
            raise TransientDependencyError()

        for _ in range(3):
            with self.assertRaises(TransientDependencyError):
                await breaker.execute(unavailable, RetrySafety())

        async def dependency() -> None:
            nonlocal dependency_calls
            dependency_calls += 1

        deadline = retry.new_deadline()
        with self.assertRaises(CircuitOpen):
            await breaker.execute(
                dependency,
                RetrySafety.read_only(),
                deadline=deadline,
                acquire_attempt_lease=lambda attempt_deadline: remote.acquire(
                    deadline=attempt_deadline
                ),
            )

        self.assertEqual(dependency_calls, 0)
        self.assertFalse(remote.executing)
        self.assertFalse(remote.waiting)

    async def test_half_open_local_rejection_preserves_elapsed_eligibility(self) -> None:
        clock = FakeClock()
        retry_sleeper = FakeSleeper(clock, auto_advance=False)
        capacity_sleeper = FakeSleeper(clock, auto_advance=False)
        retry = RetryPolicy(clock, retry_sleeper)
        breaker = CircuitBreaker(retry, clock)
        remote = self.BulkheadSet(clock, capacity_sleeper)["remote"]

        async def unavailable() -> None:
            raise TransientDependencyError()

        for _ in range(3):
            with self.assertRaises(TransientDependencyError):
                await breaker.execute(unavailable, RetrySafety())
        clock.advance(1.0)
        eligible_at = breaker.next_probe_at
        deadline = retry.new_deadline()

        executing = await remote.acquire(deadline=deadline)
        queued_task = asyncio.create_task(
            remote.acquire(deadline=deadline), name="test-half-open-capacity-waiter"
        )
        await wait_until(lambda: remote.waiting)
        dependency_calls = 0

        async def dependency() -> None:
            nonlocal dependency_calls
            dependency_calls += 1

        try:
            with self.assertRaises(self.Overloaded) as caught:
                await breaker.execute(
                    dependency,
                    RetrySafety.read_only(),
                    deadline=deadline,
                    acquire_attempt_lease=lambda attempt_deadline: remote.acquire(
                        deadline=attempt_deadline
                    ),
                )
        finally:
            queued_task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await queued_task
            executing.release()

        self.assertEqual(caught.exception.code, "overloaded")
        self.assertEqual(dependency_calls, 0)
        self.assertEqual(breaker.state, CircuitState.OPEN)
        self.assertEqual(breaker.next_probe_at, eligible_at)
        self.assertLessEqual(breaker.next_probe_at, clock())
        self.assertFalse(breaker.probe_in_flight)


class PubSubTests(unittest.TestCase):
    def setUp(self) -> None:
        (
            self.MAX_QUEUED_PER_SUBSCRIBER,
            self.MAX_SUBSCRIBERS,
            self.NoPendingEvent,
            self.PubSub,
            self.ResourceLimit,
            self.UnknownSubscriber,
        ) = load_pubsub_api()

    def test_published_pubsub_defaults_use_named_bounds(self) -> None:
        bus = self.PubSub()

        self.assertEqual(self.MAX_SUBSCRIBERS, 4)
        self.assertEqual(self.MAX_QUEUED_PER_SUBSCRIBER, 8)
        self.assertEqual(bus.max_subscribers, self.MAX_SUBSCRIBERS)
        self.assertEqual(bus.max_pending, self.MAX_QUEUED_PER_SUBSCRIBER)
        with self.assertRaises(ValueError):
            self.PubSub(max_subscribers=self.MAX_SUBSCRIBERS + 1)
        with self.assertRaises(ValueError):
            self.PubSub(max_pending=self.MAX_QUEUED_PER_SUBSCRIBER + 1)

        smaller = self.PubSub(max_subscribers=2, max_pending=3)
        self.assertEqual(smaller.max_subscribers, 2)
        self.assertEqual(smaller.max_pending, 3)

    def test_subscriber_limit_fails_closed_and_recovers(self) -> None:
        bus = self.PubSub()
        subscribers = [bus.subscribe() for _ in range(4)]

        with self.assertRaises(self.ResourceLimit) as caught:
            bus.subscribe()
        self.assertEqual(caught.exception.code, "resource_limit")
        self.assertEqual(bus.subscriber_count, 4)

        self.assertTrue(bus.unsubscribe(subscribers[0]))
        self.assertFalse(bus.unsubscribe(subscribers[0]))
        replacement = bus.subscribe()
        self.assertEqual(bus.subscriber_count, 4)
        self.assertNotIn(replacement, subscribers)

    def test_slow_subscriber_is_disconnected_without_payload_diagnostic(self) -> None:
        bus = self.PubSub()
        slow = bus.subscribe()
        secret_event = {"token": "not-for-diagnostics"}
        for index in range(8):
            result = bus.publish({"sequence": index})
            self.assertEqual(result.enqueued, (slow,))

        healthy = bus.subscribe()
        result = bus.publish(secret_event)

        self.assertEqual(result.enqueued, (healthy,))
        self.assertEqual(len(result.disconnected), 1)
        disconnected = result.disconnected[0]
        self.assertEqual(disconnected.subscriber_id, slow)
        self.assertEqual(disconnected.code, "slow_subscriber")
        self.assertEqual(disconnected.discarded_count, 8)
        self.assertNotIn("not-for-diagnostics", repr(result))
        self.assertEqual(bus.receive(healthy), secret_event)
        with self.assertRaises(self.UnknownSubscriber):
            bus.pending_count(slow)
        replacement = bus.subscribe()
        self.assertNotEqual(replacement, slow)
        self.assertEqual(bus.subscriber_count, 2)

    def test_each_subscriber_observes_its_own_fifo(self) -> None:
        bus = self.PubSub()
        first = bus.subscribe()
        second = bus.subscribe()
        for event in ("a", "b", "c"):
            result = bus.publish(event)
            self.assertEqual(result.enqueued, (first, second))

        self.assertEqual([bus.receive(first) for _ in range(3)], ["a", "b", "c"])
        self.assertEqual([bus.receive(second) for _ in range(3)], ["a", "b", "c"])
        with self.assertRaises(self.NoPendingEvent):
            bus.receive(first)

    def test_late_subscriber_has_no_replay_history(self) -> None:
        bus = self.PubSub()
        early = bus.subscribe()
        bus.publish("before")
        late = bus.subscribe()

        self.assertEqual(bus.pending_count(early), 1)
        self.assertEqual(bus.pending_count(late), 0)


class ResilienceIsolationTests(unittest.TestCase):
    def test_focused_resilience_runs_when_later_modules_are_unavailable(self) -> None:
        test_path = Path(__file__)
        tree = ast.parse(test_path.read_text(encoding="utf-8"), filename=str(test_path))
        top_level_modules = {
            node.module
            for node in tree.body
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        self.assertTrue(
            {"patterns.capacity", "patterns.pubsub"}.isdisjoint(top_level_modules)
        )

        isolated_runner = r'''
import importlib.abc
import sys
import unittest

BLOCKED = {"patterns.capacity", "patterns.pubsub"}

class LaterCheckpointBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in BLOCKED:
            raise ModuleNotFoundError(f"blocked later checkpoint: {fullname}")
        return None

sys.meta_path.insert(0, LaterCheckpointBlocker())
import test_network_patterns as network_tests

loader = unittest.TestLoader()
suite = unittest.TestSuite(
    (
        loader.loadTestsFromTestCase(network_tests.RetryPolicyTests),
        loader.loadTestsFromTestCase(network_tests.CircuitBreakerTests),
    )
)
result = unittest.TextTestRunner(verbosity=0).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
if BLOCKED.intersection(sys.modules):
    raise SystemExit("a later checkpoint was imported")
'''
        completed = subprocess.run(
            [sys.executable, "-B", "-c", isolated_runner],
            cwd=test_path.parent,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stdout + completed.stderr,
        )


class SourceBoundaryTests(unittest.TestCase):
    def test_network_pattern_companions_import_no_transport_or_thread_api(self) -> None:
        forbidden = {"socket", "ssl", "selectors", "threading", "subprocess", "time"}
        for name in ("resilience.py", "capacity.py", "pubsub.py"):
            path = EXAMPLES / "patterns" / name
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imported: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            self.assertTrue(forbidden.isdisjoint(imported), f"forbidden import in {name}")

    def test_pubsub_owns_no_background_task(self) -> None:
        path = EXAMPLES / "patterns" / "pubsub.py"
        source = path.read_text(encoding="utf-8")
        self.assertNotIn("asyncio", source)
        self.assertNotIn("create_task", source)


if __name__ == "__main__":
    unittest.main()
