"""Offline contract tests for Appendix C's direct and core pattern routes."""

import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


APPENDIX_DIR = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = APPENDIX_DIR / "_shared"
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

from patterns.architecture import (  # noqa: E402
    FixedClock,
    InMemoryExecutionAdapter,
    ListOutput,
    SequenceIds,
    compose_application,
)
from patterns.direct import (  # noqa: E402
    run,
    shipping_cost_direct,
    transfer_decision,
)
from patterns.domain import (  # noqa: E402
    DecisionRecord,
    ExecutionBoundaryError,
    InvalidDecisionRecord,
    InvalidJob,
    Job,
    PatternError,
    Result,
    UnknownSelection,
)
from patterns.essential import (  # noqa: E402
    DirectExecutor,
    LegacyRunnerAdapter,
    LegacyRunnerError,
    LegacyRunnerFake,
    build_executor,
    express_shipping,
    keep_payload,
    run_with_policy,
    select_policy,
    shipping_cost_with_policy,
    standard_shipping,
)
from patterns.professional import (  # noqa: E402
    JobEventSubject,
    MeasuringExecutor,
    ObserverLimitError,
)


class ValuesClock:
    """Return deterministic values in the order a Decorator requests them."""

    def __init__(self, values):
        self.values = iter(values)

    def __call__(self):
        return next(self.values)


class CorePatternTests(unittest.TestCase):
    def test_core_01_direct_happy_path_keeps_job_unchanged(self):
        job = Job("job-1", "alpha")
        before = (job.job_id, job.payload)

        result = run(job)

        self.assertEqual(
            result,
            Result("job-1", "completed", "processed:alpha"),
        )
        self.assertEqual((job.job_id, job.payload), before)

    def test_core_02_direct_boundaries_and_recovery(self):
        boundary = Job("j" * 32, "p" * 256)
        self.assertEqual(run(boundary).job_id, "j" * 32)

        for bad_id, bad_payload in (("j" * 33, "ok"), ("ok", "p" * 257)):
            with self.subTest(bad_id=len(bad_id), bad_payload=len(bad_payload)):
                with self.assertRaises(InvalidJob) as raised:
                    Job(bad_id, bad_payload)
                self.assertEqual(raised.exception.code, "invalid_job")

        with self.assertRaises(InvalidJob) as raised:
            run("not-a-job")
        self.assertEqual(raised.exception.code, "invalid_job")
        self.assertEqual(run(Job("recovered", "ok")).status, "completed")

    def test_core_03_import_is_quiet_isolated_and_residue_free(self):
        script = (
            "import sys; "
            f"sys.path.insert(0, {str(EXAMPLES_DIR)!r}); "
            "import patterns; "
            "import patterns.domain, patterns.direct, patterns.essential; "
            "import patterns.professional, patterns.architecture; "
            "print('import-ok')"
        )
        environment = {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
        }
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [sys.executable, "-I", "-B", "-c", script],
                cwd=directory,
                env=environment,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            residue = list(Path(directory).iterdir())

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "import-ok\n")
        self.assertEqual(completed.stderr, "")
        self.assertEqual(residue, [])

    def test_core_04_decision_record_accepts_direct_and_pattern_choices(self):
        direct_record = transfer_decision()
        pattern_record = transfer_decision("Strategy")

        self.assertIsNone(direct_record.pattern)
        self.assertEqual(pattern_record.pattern, "Strategy")
        self.assertEqual(
            tuple(direct_record.as_dict()),
            (
                "problem",
                "forces",
                "simplest_option",
                "pattern",
                "cost",
                "expected_failure",
                "verification",
                "remove_when",
            ),
        )
        self.assertEqual(
            tuple(pattern_record.as_dict()),
            tuple(direct_record.as_dict()),
        )

        with self.assertRaises(UnknownSelection) as raised:
            transfer_decision("Factory")
        self.assertEqual(raised.exception.code, "unknown_selection")

    def test_core_05_incomplete_decision_record_recovers(self):
        values = {
            "problem": "choose a formatter",
            "forces": ("the caller owns the format",),
            "simplest_option": "one function",
            "pattern": None,
            "cost": "one conditional",
            "expected_failure": "an unknown format is rejected",
            "verification": "contract tests pass",
            "remove_when": "keep direct code while one format exists",
        }
        broken = dict(values)
        broken["forces"] = ()

        with self.assertRaises(InvalidDecisionRecord) as raised:
            DecisionRecord(**broken)
        self.assertEqual(raised.exception.code, "invalid_decision_record")
        self.assertEqual(DecisionRecord(**values).pattern, None)

    def test_core_06_transfer_direct_and_strategy_contracts_match(self):
        for distance in (0, 100):
            with self.subTest(distance=distance):
                self.assertEqual(
                    shipping_cost_direct(distance),
                    shipping_cost_with_policy(distance, standard_shipping),
                )
                self.assertEqual(
                    shipping_cost_direct(distance, express=True),
                    shipping_cost_with_policy(distance, express_shipping),
                )

        with self.assertRaises(PatternError) as raised:
            shipping_cost_direct(101)
        self.assertEqual(raised.exception.code, "invalid_distance")
        self.assertEqual(shipping_cost_direct(1), 6)

    def test_core_07_strategy_selection_execution_and_injected_fake(self):
        job = Job("job-2", "mixed")
        self.assertEqual(run_with_policy(job, keep_payload), run(job))
        self.assertEqual(
            run_with_policy(job, select_policy("uppercase")).output,
            "processed:MIXED",
        )

        calls = []

        def reverse_policy(selected_job):
            calls.append(selected_job.job_id)
            return Job(selected_job.job_id, selected_job.payload[::-1])

        self.assertEqual(
            run_with_policy(job, reverse_policy).output,
            "processed:dexim",
        )
        self.assertEqual(calls, ["job-2"])

        with self.assertRaises(UnknownSelection) as raised:
            select_policy("missing")
        self.assertEqual(raised.exception.code, "unknown_selection")
        self.assertIs(select_policy("keep"), keep_payload)

    def test_core_08_function_factory_validates_before_construction(self):
        job = Job("job-3", "quiet")
        self.assertEqual(
            build_executor("direct").execute(job),
            DirectExecutor().execute(job),
        )
        self.assertEqual(
            build_executor("uppercase").execute(job).output,
            "processed:QUIET",
        )

        with self.assertRaises(UnknownSelection) as raised:
            build_executor("global-singleton")
        self.assertEqual(raised.exception.code, "unknown_selection")
        self.assertEqual(build_executor("direct").execute(job), run(job))

    def test_core_09_adapter_translates_data_method_and_failure(self):
        job = Job("job-4", "legacy")
        legacy = LegacyRunnerFake()
        adapter = LegacyRunnerAdapter(legacy)

        self.assertEqual(adapter.execute(job), run(job))
        self.assertEqual(legacy.calls, [("job-4", "legacy")])

        failure = LegacyRunnerError("offline")
        legacy.failure = failure
        with self.assertRaises(ExecutionBoundaryError) as raised:
            adapter.execute(job)
        self.assertEqual(raised.exception.code, "legacy_failure")
        self.assertIs(raised.exception.__cause__, failure)

        legacy.failure = None
        self.assertEqual(adapter.execute(job), run(job))

    def test_core_10_adapter_rejects_malformed_reply_and_recovers(self):
        job = Job("job-5", "shape")
        legacy = LegacyRunnerFake(response={"state": "DONE"})
        adapter = LegacyRunnerAdapter(legacy)

        with self.assertRaises(ExecutionBoundaryError) as raised:
            adapter.execute(job)
        self.assertEqual(raised.exception.code, "invalid_legacy_result")

        legacy.response = None
        self.assertEqual(adapter.execute(job), run(job))

    def test_core_11_decorator_preserves_result_and_exposes_order(self):
        job = Job("job-6", "measure")
        events = []
        measurements = []
        clock = ValuesClock([0, 1, 3, 5])
        inner = MeasuringExecutor(
            DirectExecutor(),
            label="inner",
            clock=clock,
            events=events,
            measurements=measurements,
        )
        outer = MeasuringExecutor(
            inner,
            label="outer",
            clock=clock,
            events=events,
            measurements=measurements,
        )

        result = outer.execute(job)

        self.assertEqual(result, run(job))
        self.assertEqual(
            events,
            ["outer:before", "inner:before", "inner:after", "outer:after"],
        )
        self.assertEqual(
            measurements,
            [("inner", "completed", 2), ("outer", "completed", 5)],
        )

    def test_core_12_decorator_preserves_declared_failure_identity(self):
        failure = ExecutionBoundaryError("declared_failure", "expected")

        class FailingExecutor:
            def execute(self, job):
                raise failure

        events = []
        measurements = []
        wrapped = MeasuringExecutor(
            FailingExecutor(),
            label="measure",
            clock=ValuesClock([10, 13]),
            events=events,
            measurements=measurements,
        )

        with self.assertRaises(ExecutionBoundaryError) as raised:
            wrapped.execute(Job("job-7", "fail"))
        self.assertIs(raised.exception, failure)
        self.assertEqual(events, ["measure:before", "measure:error"])
        self.assertEqual(measurements, [("measure", "error", 3)])

    def test_core_13_observer_cap_unsubscribe_and_recovery(self):
        subject = JobEventSubject(limit=2)
        first = subject.subscribe(lambda result: None)
        second = subject.subscribe(lambda result: None)

        with self.assertRaises(ObserverLimitError) as raised:
            subject.subscribe(lambda result: None)
        self.assertEqual(raised.exception.code, "observer_limit")
        self.assertEqual(subject.active_count, 2)

        self.assertTrue(first.unsubscribe())
        self.assertFalse(first.unsubscribe())
        third = subject.subscribe(lambda result: None)
        self.assertFalse(first.active)
        self.assertTrue(second.active)
        self.assertTrue(third.active)

    def test_core_14_observer_snapshot_is_stable_during_removal(self):
        subject = JobEventSubject(limit=3)
        calls = []
        second = None

        def remove_second(result):
            calls.append("first")
            second.unsubscribe()

        subject.subscribe(remove_second)
        second = subject.subscribe(lambda result: calls.append("second"))

        first_report = subject.publish(run(Job("job-8", "event")))
        second_report = subject.publish(run(Job("job-9", "next")))

        self.assertEqual(calls, ["first", "second", "first"])
        self.assertEqual(len(first_report.notified), 2)
        self.assertEqual(len(second_report.notified), 1)
        self.assertFalse(second.active)

    def test_core_15_observer_failure_is_isolated_without_history(self):
        subject = JobEventSubject(limit=2)
        received = []

        def broken(result):
            raise RuntimeError("private callback detail")

        broken_subscription = subject.subscribe(broken)
        subject.subscribe(lambda result: received.append(result.job_id))
        event = run(Job("job-10", "notify"))

        report = subject.publish(event)

        self.assertEqual(received, ["job-10"])
        self.assertEqual(len(report.failures), 1)
        self.assertEqual(report.failures[0].code, "observer_failed")
        self.assertFalse(broken_subscription.active)
        self.assertEqual(subject.active_count, 1)
        self.assertNotIn("history", vars(subject))
        self.assertNotIn(event, vars(subject).values())

    def test_core_16_composition_root_owns_deterministic_dependencies(self):
        output = ListOutput()
        application = compose_application(
            execution_port=InMemoryExecutionAdapter(),
            new_id=SequenceIds(["job-11"]),
            clock=FixedClock(12.5),
            write=output,
        )

        result = application.submit("composed")

        self.assertEqual(result, run(Job("job-11", "composed")))
        self.assertEqual(output.messages, ["12.500|job-11|completed"])

    def test_core_17_changing_adapter_keeps_application_contract(self):
        class AlternateExecutionAdapter:
            def __init__(self):
                self.calls = []

            def execute(self, job):
                self.calls.append(job)
                return run(job)

        alternate = AlternateExecutionAdapter()
        output = ListOutput()
        application = compose_application(
            execution_port=alternate,
            new_id=SequenceIds(["job-12"]),
            clock=FixedClock(3),
            write=output,
        )

        result = application.submit("portable")

        self.assertEqual(result, run(Job("job-12", "portable")))
        self.assertEqual(alternate.calls, [Job("job-12", "portable")])
        self.assertEqual(output.messages, ["3.000|job-12|completed"])

    def test_core_18_invalid_submission_consumes_no_id_and_recovers(self):
        identifiers = SequenceIds(["job-13"])
        output = ListOutput()
        application = compose_application(
            execution_port=InMemoryExecutionAdapter(),
            new_id=identifiers,
            clock=FixedClock(0),
            write=output,
        )

        with self.assertRaises(InvalidJob) as raised:
            application.submit("")
        self.assertEqual(raised.exception.code, "invalid_job")
        self.assertEqual(identifiers.position, 0)
        self.assertEqual(output.messages, [])

        self.assertEqual(application.submit("recovered").job_id, "job-13")

    def test_core_19_exhausted_id_source_is_stable_and_fresh_root_recovers(self):
        first_output = ListOutput()
        application = compose_application(
            execution_port=InMemoryExecutionAdapter(),
            new_id=SequenceIds(["job-once"]),
            clock=FixedClock(1),
            write=first_output,
        )
        self.assertEqual(application.submit("first").job_id, "job-once")

        with self.assertRaises(PatternError) as raised:
            application.submit("second")
        self.assertEqual(raised.exception.code, "id_source_exhausted")
        self.assertEqual(first_output.messages, ["1.000|job-once|completed"])

        recovered_output = ListOutput()
        recovered = compose_application(
            execution_port=InMemoryExecutionAdapter(),
            new_id=SequenceIds(["job-fresh"]),
            clock=FixedClock(2),
            write=recovered_output,
        )
        self.assertEqual(recovered.submit("recovered").job_id, "job-fresh")
        self.assertEqual(recovered_output.messages, ["2.000|job-fresh|completed"])

    def test_core_20_invalid_port_result_is_translated_and_root_recovers(self):
        class MismatchedExecutionPort:
            def execute(self, job):
                return Result("another-job", "completed", "wrong owner")

        rejected_output = ListOutput()
        application = compose_application(
            execution_port=MismatchedExecutionPort(),
            new_id=SequenceIds(["job-owned"]),
            clock=FixedClock(3),
            write=rejected_output,
        )

        with self.assertRaises(ExecutionBoundaryError) as raised:
            application.submit("boundary")
        self.assertEqual(raised.exception.code, "invalid_execution_result")
        self.assertEqual(rejected_output.messages, [])

        recovered = compose_application(
            execution_port=InMemoryExecutionAdapter(),
            new_id=SequenceIds(["job-recovered"]),
            clock=FixedClock(4),
            write=ListOutput(),
        )
        self.assertEqual(recovered.submit("ok").job_id, "job-recovered")

    def test_core_21_core_modules_keep_forbidden_dependencies_out(self):
        core_modules = (
            "domain.py",
            "direct.py",
            "essential.py",
            "professional.py",
            "architecture.py",
        )
        forbidden = {"asyncio", "dataclasses", "requests", "socket"}

        for module_name in core_modules:
            with self.subTest(module=module_name):
                source = (EXAMPLES_DIR / "patterns" / module_name).read_text(
                    encoding="utf-8"
                )
                tree = ast.parse(source)
                imported = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.update(
                            alias.name.split(".", maxsplit=1)[0]
                            for alias in node.names
                        )
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported.add(node.module.split(".", maxsplit=1)[0])
                self.assertEqual(imported & forbidden, set())
                self.assertNotIn("Protocol", source)


if __name__ == "__main__":
    unittest.main()
