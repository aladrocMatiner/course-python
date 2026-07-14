from __future__ import annotations

import copy
import importlib.util
import inspect
import json
import os
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "run_quality.py"
SPEC = importlib.util.spec_from_file_location("run_quality", MODULE_PATH)
assert SPEC and SPEC.loader
run_quality = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = run_quality
SPEC.loader.exec_module(run_quality)


def valid_payload() -> dict[str, object]:
    return tomllib.loads((ROOT / "tools" / "quality_matrix.toml").read_text(encoding="utf-8"))


class MatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="quality-matrix-test-")
        self.root = Path(self.temporary.name)
        for relative in (
            "chapter-23-network-programming/tools/bookcheck_plugin.py",
            "chapter-24-python-cpp-integration/tools/bookcheck_plugin.py",
            "chapter-25-python-rust-integration/tools/bookcheck_plugin.py",
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("def register(registry): pass\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def parse(self, payload: dict[str, object] | None = None):
        return run_quality.parse_matrix(payload or valid_payload(), self.root)

    def test_repository_matrix_has_exact_ordered_profiles(self) -> None:
        matrix = run_quality.load_matrix(ROOT / "tools" / "quality_matrix.toml", ROOT)
        self.assertEqual(
            ("tool-tests", "curriculum", "parity", "book-generic"),
            matrix.profiles["core"],
        )
        self.assertEqual(("network-domain",), matrix.profiles["network-domain"])
        self.assertEqual(("cpp-domain",), matrix.profiles["cpp-domain"])
        self.assertEqual(("rust-domain",), matrix.profiles["rust-domain"])
        self.assertEqual(tuple(item.id for item in matrix.checks), matrix.profiles["handoff"])
        self.assertEqual(
            {
                "network-domain": "chapter-23-network-programming/tools/bookcheck_plugin.py",
                "cpp-domain": "chapter-24-python-cpp-integration/tools/bookcheck_plugin.py",
                "rust-domain": "chapter-25-python-rust-integration/tools/bookcheck_plugin.py",
            },
            {
                item.id: item.plugin_path
                for item in matrix.checks
                if item.adapter == "book-plugin"
            },
        )

    def test_valid_matrix_is_parsed_without_executable_argv(self) -> None:
        matrix = self.parse()
        self.assertEqual(
            ("tool-tests", "curriculum", "parity", "book-generic"),
            matrix.profiles["core"],
        )
        self.assertEqual("book-plugin", matrix.by_id["network-domain"].adapter)

    def test_unknown_schema_keys_adapters_and_arbitrary_argv_fail_closed(self) -> None:
        cases: list[tuple[str, object]] = [
            ("mystery", True),
            ("schema_version", 99),
        ]
        for key, value in cases:
            with self.subTest(key=key):
                payload = valid_payload()
                payload[key] = value
                with self.assertRaises(run_quality.MatrixError):
                    self.parse(payload)

        payload = valid_payload()
        payload["checks"][0]["adapter"] = "shell"  # type: ignore[index]
        with self.assertRaisesRegex(run_quality.MatrixError, "unknown adapter"):
            self.parse(payload)

        payload = valid_payload()
        payload["checks"][0]["argv"] = ["sh", "-c", "true"]  # type: ignore[index]
        with self.assertRaisesRegex(run_quality.MatrixError, "unknown keys"):
            self.parse(payload)

    def test_duplicate_missing_wildcard_and_out_of_order_profiles_fail(self) -> None:
        payload = valid_payload()
        payload["checks"].append(copy.deepcopy(payload["checks"][0]))  # type: ignore[union-attr,index]
        with self.assertRaisesRegex(run_quality.MatrixError, "duplicate check"):
            self.parse(payload)

        for profile in (["missing"], ["*"], ["curriculum", "tool-tests"]):
            with self.subTest(profile=profile):
                payload = valid_payload()
                payload["profiles"]["core"] = profile  # type: ignore[index]
                with self.assertRaises(run_quality.MatrixError):
                    self.parse(payload)

    def test_invalid_prerequisites_and_bounds_fail(self) -> None:
        payload = valid_payload()
        payload["checks"][0]["prerequisites"] = ["git", "git"]  # type: ignore[index]
        with self.assertRaisesRegex(run_quality.MatrixError, "duplicates"):
            self.parse(payload)

        payload = valid_payload()
        payload["checks"][0]["prerequisites"] = ["../git"]  # type: ignore[index]
        with self.assertRaisesRegex(run_quality.MatrixError, "prerequisites"):
            self.parse(payload)

        for key, value in (
            ("hard_timeout_seconds", run_quality.MAX_TIMEOUT_SECONDS + 1),
            ("hard_output_limit_bytes", run_quality.MAX_OUTPUT_LIMIT_BYTES + 1),
            ("snapshot_limit_bytes", run_quality.MAX_SNAPSHOT_LIMIT_BYTES + 1),
        ):
            with self.subTest(key=key):
                payload = valid_payload()
                payload[key] = value
                with self.assertRaises(run_quality.MatrixError):
                    self.parse(payload)

    def test_public_contract_fields_reject_secrets_paths_and_terminal_controls(self) -> None:
        unsafe_values = (
            "\x1b[31mterminal-controlled scope\x1b[0m",
            "OPENAI_API_KEY=sk-fixture-secret-value",
            "Details at /tmp/My Project/private.txt",
            r"Details at C:\Program Files\Private\notes.txt",
            r"Details at \\server\Shared Folder\private.txt",
        )
        for field in ("evidence_scope", "human_review_boundary"):
            for unsafe in unsafe_values:
                with self.subTest(field=field, unsafe=unsafe):
                    payload = valid_payload()
                    payload[field] = unsafe
                    with self.assertRaises(run_quality.MatrixError) as caught:
                        self.parse(payload)
                    self.assertNotIn(unsafe, str(caught.exception))

        for unsafe in unsafe_values:
            with self.subTest(field="check.evidence_scope", unsafe=unsafe):
                payload = valid_payload()
                payload["checks"][0]["evidence_scope"] = unsafe  # type: ignore[index]
                with self.assertRaises(run_quality.MatrixError) as caught:
                    self.parse(payload)
                self.assertNotIn(unsafe, str(caught.exception))

    def test_plugin_path_escape_and_unsafe_symlink_fail(self) -> None:
        payload = valid_payload()
        network = next(item for item in payload["checks"] if item["id"] == "network-domain")  # type: ignore[union-attr]
        network["plugin_path"] = "../plugin.py"
        with self.assertRaisesRegex(run_quality.MatrixError, "escapes"):
            self.parse(payload)

        outside = self.root.parent / f"outside-{self.root.name}.py"
        outside.write_text("pass\n", encoding="utf-8")
        try:
            link = self.root / "escape.py"
            try:
                link.symlink_to(outside)
            except OSError:
                self.skipTest("symlinks unavailable")
            payload = valid_payload()
            network = next(item for item in payload["checks"] if item["id"] == "network-domain")  # type: ignore[union-attr]
            network["plugin_path"] = "escape.py"
            with self.assertRaisesRegex(run_quality.MatrixError, "escapes"):
                self.parse(payload)
        finally:
            outside.unlink(missing_ok=True)

    def test_required_core_domain_and_handoff_contracts_cannot_be_weakened(self) -> None:
        mutations = []

        def without_tool_tests(payload):
            payload["profiles"]["core"] = ["curriculum", "parity", "book-generic"]

        mutations.append(without_tool_tests)

        def widened_domain(payload):
            payload["profiles"]["network-domain"] = ["network-domain", "cpp-domain"]

        mutations.append(widened_domain)

        def incomplete_handoff(payload):
            payload["profiles"]["handoff"] = payload["profiles"]["handoff"][:-1]

        mutations.append(incomplete_handoff)

        def adapter_swap(payload):
            next(item for item in payload["checks"] if item["id"] == "tool-tests")["adapter"] = "parity"

        mutations.append(adapter_swap)

        for mutation in mutations:
            with self.subTest(mutation=mutation.__name__):
                payload = valid_payload()
                mutation(payload)
                with self.assertRaisesRegex(run_quality.MatrixError, "required .* contract"):
                    self.parse(payload)


class SelectionAndAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = run_quality.load_matrix(ROOT / "tools" / "quality_matrix.toml", ROOT)

    def test_default_and_explicit_selection_are_deterministic(self) -> None:
        mode, selected, changed = run_quality.resolve_selection(self.matrix, None, [], None)
        self.assertEqual("core", mode)
        self.assertEqual(self.matrix.profiles["core"], selected)
        self.assertIsNone(changed)

        mode, selected, _ = run_quality.resolve_selection(
            self.matrix, None, ["rust-domain", "curriculum"], None
        )
        self.assertEqual("explicit", mode)
        self.assertEqual(("curriculum", "rust-domain"), selected)

    def test_invalid_or_mutually_exclusive_selection_fails_before_execution(self) -> None:
        with self.assertRaisesRegex(run_quality.MatrixError, "mutually exclusive"):
            run_quality.resolve_selection(self.matrix, "core", ["curriculum"], None)
        with self.assertRaisesRegex(run_quality.MatrixError, "unknown profile"):
            run_quality.resolve_selection(self.matrix, "missing", [], None)
        with self.assertRaisesRegex(run_quality.MatrixError, "unknown check"):
            run_quality.resolve_selection(self.matrix, None, ["missing"], None)
        with self.assertRaisesRegex(run_quality.MatrixError, "same check"):
            run_quality.resolve_selection(self.matrix, None, ["curriculum", "curriculum"], None)

    def test_changed_scope_reaches_only_generic_book_adapter(self) -> None:
        _, selected, revision = run_quality.resolve_selection(
            self.matrix, "core", [], "origin/main"
        )
        self.assertIn("book-generic", selected)
        generic = run_quality.build_argv(self.matrix.by_id["book-generic"], revision)
        plugin = run_quality.build_argv(self.matrix.by_id["network-domain"], revision)
        self.assertEqual(["--changed-from", "origin/main"], generic[-2:])
        self.assertNotIn("--changed-from", plugin)
        with self.assertRaisesRegex(run_quality.MatrixError, "generic book"):
            run_quality.resolve_selection(self.matrix, "network-domain", [], "origin/main")
        with self.assertRaisesRegex(run_quality.MatrixError, "safe Git revision"):
            run_quality.resolve_selection(self.matrix, "core", [], "--all")

    def test_closed_adapters_build_exact_argv_without_shell(self) -> None:
        commands = {
            item.id: run_quality.build_argv(item)
            for item in self.matrix.checks
        }
        self.assertEqual(
            ["openspec", "validate", "--changes", "--strict", "--no-interactive"],
            commands["openspec-strict"],
        )
        self.assertEqual(["git", "diff", "--check", "HEAD"], commands["whitespace"])
        self.assertEqual(
            "chapter-23-network-programming/tools/bookcheck_plugin.py",
            commands["network-domain"][-1],
        )
        source = inspect.getsource(run_quality._run_child_under_subreaper)
        self.assertIn("shell=False", source)
        self.assertIn("stdin=subprocess.DEVNULL", source)
        self.assertIn("stdout=subprocess.PIPE", source)
        self.assertNotIn("combined-output", source)


class ExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="quality-execution-test-")
        self.root = Path(self.temporary.name)
        (self.root / "source.txt").write_text("original\n", encoding="utf-8")
        self.check = run_quality.Check(
            id="fixture",
            adapter="curriculum",
            timeout_seconds=2,
            output_limit_bytes=4096,
            prerequisites=(),
            evidence_scope="Fixture evidence.",
        )
        self.matrix = run_quality.Matrix(
            checks=(self.check,),
            profiles={"core": ("fixture",)},
            hard_timeout_seconds=10,
            hard_output_limit_bytes=65536,
            snapshot_limit_bytes=1048576,
            evidence_scope="Automated fixture evidence.",
            human_review_boundary="Human gates remain pending.",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @unittest.skipUnless(run_quality.process_tree_supported(), "requires Linux subreaper containment")
    def test_child_success_crash_timeout_and_output_overflow(self) -> None:
        success = run_quality.run_child(
            self.root, [sys.executable, "-c", "print('ok')"], 2, 1024
        )
        self.assertEqual(0, success.returncode)
        self.assertIsNone(success.infrastructure_error)
        self.assertEqual(3, success.observed_output_bytes)

        crash = run_quality.run_child(
            self.root, [sys.executable, "-c", "raise SystemExit(3)"], 2, 1024
        )
        self.assertEqual(3, crash.returncode)

        timeout = run_quality.run_child(
            self.root, [sys.executable, "-c", "import time; time.sleep(5)"], 0.05, 1024
        )
        self.assertIn("timeout", timeout.infrastructure_error or "")

        overflow = run_quality.run_child(
            self.root,
            [sys.executable, "-c", "import os; os.write(1, b'x' * 100000)"],
            2,
            128,
        )
        self.assertIn("output", overflow.infrastructure_error or "")
        self.assertEqual(128, overflow.observed_output_bytes)
        self.assertFalse(any(path.name.startswith("course-quality-run-") for path in self.root.iterdir()))

    @unittest.skipUnless(run_quality.process_tree_supported(), "requires Linux subreaper containment")
    def test_setsid_descendant_is_adopted_killed_and_cannot_write_late(self) -> None:
        late_path = self.root / "late-write.txt"
        ready_path = self.root / "detached-ready.txt"
        release_path = self.root / "detached-release.txt"
        descendant = f"""
import os
import signal
import time
from pathlib import Path

late = Path({str(late_path)!r})
ready = Path({str(ready_path)!r})
ready_staging = ready.with_suffix(".tmp")
release = Path({str(release_path)!r})

def attempt_late_write(_signum, _frame):
    late.write_text("signal-handler-ran", encoding="utf-8")

signal.signal(signal.SIGTERM, attempt_late_write)
ready_staging.write_text(str(os.getpid()), encoding="ascii")
os.replace(ready_staging, ready)
for descriptor in (0, 1, 2):
    try:
        os.close(descriptor)
    except OSError:
        pass
deadline = time.monotonic() + 5.0
while time.monotonic() < deadline and not release.exists():
    time.sleep(0.01)
if release.exists():
    late.write_text("survived-result", encoding="utf-8")
"""
        code = f"""
import subprocess
import sys
import time
from pathlib import Path

ready = Path({str(ready_path)!r})
subprocess.Popen(
    [sys.executable, "-c", {descendant!r}],
    start_new_session=True,
    close_fds=True,
)
deadline = time.monotonic() + 1.0
while time.monotonic() < deadline and not ready.exists():
    time.sleep(0.01)
if not ready.exists():
    raise SystemExit(4)
"""
        outcome = run_quality.run_child(self.root, [sys.executable, "-c", code], 2, 1024)
        self.assertIn("descendant", outcome.infrastructure_error or "")
        self.assertNotIn("did not converge", outcome.infrastructure_error or "")
        descendant_pid = int(ready_path.read_text(encoding="ascii"))
        self.assertFalse(run_quality._pid_alive(descendant_pid))
        self.assertFalse(late_path.exists())
        release_path.write_text("release", encoding="ascii")
        self.assertFalse(late_path.exists())

        recovery = run_quality.run_child(
            self.root, [sys.executable, "-c", "raise SystemExit(0)"], 2, 1024
        )
        self.assertEqual(0, recovery.returncode)
        self.assertIsNone(recovery.infrastructure_error)

    @unittest.skipUnless(run_quality.process_tree_supported(), "requires Linux signals")
    def test_cleanup_freezes_newly_observed_fork_before_kill(self) -> None:
        class FakeProcess:
            pid = 100
            done = False

            def poll(self):
                return 0 if self.done else None

            def wait(self, timeout):
                self.done = True
                return 0

        process = FakeProcess()
        observed = iter(
            (
                {101},
                {101, 102},
                {101, 102},
                {101, 102},
                {101, 102},
                set(),
                set(),
                set(),
            )
        )
        delivered: list[tuple[int, set[int]]] = []

        def record_signal(pids, chosen_signal):
            delivered.append((chosen_signal, set(pids)))
            if chosen_signal == run_quality.signal.SIGKILL and process.pid in pids:
                process.done = True

        with (
            mock.patch.object(run_quality, "_pid_alive", return_value=True),
            mock.patch.object(run_quality, "_owned_processes", side_effect=lambda *_: next(observed)),
            mock.patch.object(run_quality, "_signal_processes", side_effect=record_signal),
        ):
            contained, observable = run_quality._terminate_owned_tree(
                process, set(), {101}
            )

        self.assertTrue(contained)
        self.assertTrue(observable)
        self.assertEqual(run_quality.signal.SIGSTOP, delivered[0][0])
        first_kill = next(
            index
            for index, (chosen_signal, _) in enumerate(delivered)
            if chosen_signal == run_quality.signal.SIGKILL
        )
        self.assertTrue(
            any(
                chosen_signal == run_quality.signal.SIGSTOP and 102 in pids
                for chosen_signal, pids in delivered[:first_kill]
            )
        )
        self.assertIn(102, delivered[first_kill][1])
        self.assertNotIn(
            run_quality.signal.SIGTERM,
            [chosen_signal for chosen_signal, _ in delivered],
        )

    @unittest.skipUnless(run_quality.process_tree_supported(), "requires Linux subreaper containment")
    def test_empty_first_process_map_fails_before_execution_then_recovers(self) -> None:
        marker = self.root / "must-not-run.txt"
        command = [
            sys.executable,
            "-c",
            f"open({str(marker)!r}, 'w', encoding='utf-8').write('ran')",
        ]
        with (
            mock.patch.object(run_quality, "process_tree_supported", return_value=True),
            mock.patch.object(run_quality, "_proc_parent_map", return_value={}),
        ):
            outcome = run_quality.run_child(self.root, command, 2, 1024)
        self.assertIsNone(outcome.returncode)
        self.assertIn("current PID is absent", outcome.infrastructure_error or "")
        self.assertFalse(marker.exists())

        recovery = run_quality.run_child(
            self.root, [sys.executable, "-c", "raise SystemExit(0)"], 2, 1024
        )
        self.assertEqual(0, recovery.returncode)
        self.assertIsNone(recovery.infrastructure_error)

    @unittest.skipUnless(run_quality.process_tree_supported(), "requires Linux subreaper containment")
    def test_dynamic_process_map_loss_kills_known_setsid_writer_and_recovers(self) -> None:
        late_path = self.root / "lost-observability-late-write.txt"
        descendant = f"""
import os
import signal
import time

for descriptor in (0, 1, 2):
    try:
        os.close(descriptor)
    except OSError:
        pass
signal.signal(signal.SIGTERM, signal.SIG_IGN)
time.sleep(0.8)
open({str(late_path)!r}, "w", encoding="utf-8").write("late")
"""
        parent = (
            "import subprocess, sys, time; "
            f"subprocess.Popen([sys.executable, '-c', {descendant!r}], "
            "start_new_session=True, close_fds=True); "
            "time.sleep(0.2)"
        )
        original_map = run_quality._observable_parent_map
        original_owned = run_quality._owned_processes
        state: dict[str, set[int]] = {"captured": set()}

        def partial_map_after_capture():
            parents = original_map()
            for pid in state["captured"]:
                parents.pop(pid, None)
            return parents

        def remember_before_partial_loss(direct_pid, baseline_children, known):
            owned = original_owned(direct_pid, baseline_children, known)
            if owned and not state["captured"]:
                state["captured"].update(owned)
            return owned

        with (
            mock.patch.object(
                run_quality, "_observable_parent_map", side_effect=partial_map_after_capture
            ),
            mock.patch.object(
                run_quality,
                "_owned_processes",
                side_effect=remember_before_partial_loss,
            ),
        ):
            outcome = run_quality.run_child(
                self.root, [sys.executable, "-c", parent], 2, 1024
            )
        self.assertTrue(state["captured"], "fixture must observe the detached writer first")
        self.assertIsNone(outcome.returncode)
        self.assertIn("process observability failed", outcome.infrastructure_error or "")
        self.assertIn("cannot be proven", outcome.infrastructure_error or "")

        recovery = run_quality.run_child(
            self.root, [sys.executable, "-c", "raise SystemExit(0)"], 2, 1024
        )
        self.assertEqual(0, recovery.returncode)
        self.assertIsNone(recovery.infrastructure_error)
        time.sleep(0.9)
        self.assertFalse(late_path.exists())

    def test_partial_map_cannot_drop_live_direct_or_known_pids(self) -> None:
        owner = os.getpid()
        direct = owner + 100_000
        known_pid = owner + 100_001

        with (
            mock.patch.object(
                run_quality, "_observable_parent_map", return_value={owner: os.getppid()}
            ),
            mock.patch.object(
                run_quality, "_pid_alive", side_effect=lambda pid: pid == direct
            ),
        ):
            with self.assertRaisesRegex(run_quality.RunnerError, "live direct child"):
                run_quality._owned_processes(direct, set(), set())

        known = {known_pid}
        with (
            mock.patch.object(
                run_quality,
                "_observable_parent_map",
                return_value={owner: os.getppid(), direct: owner},
            ),
            mock.patch.object(
                run_quality, "_pid_alive", side_effect=lambda pid: pid == known_pid
            ),
        ):
            with self.assertRaisesRegex(run_quality.RunnerError, "live known descendant"):
                run_quality._owned_processes(direct, set(), known)
        self.assertEqual({known_pid}, known)

    @unittest.skipUnless(run_quality.process_tree_supported(), "requires Linux subreaper containment")
    def test_malicious_tmpdir_cannot_move_runner_temporaries_into_repository(self) -> None:
        malicious = self.root / "attacker-controlled-temp"
        malicious.mkdir()
        command = [
            sys.executable,
            "-c",
            "import tempfile; tempfile.NamedTemporaryFile(delete=False).write(b'x')",
        ]
        with mock.patch.dict(os.environ, {"TMPDIR": str(malicious)}, clear=False):
            outcome = run_quality.run_child(self.root, command, 2, 1024)
        self.assertEqual(0, outcome.returncode)
        self.assertEqual([], list(malicious.iterdir()))

    def test_minimal_environment_does_not_forward_openai_credentials(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "sk-parent-secret", "PATH": os.environ.get("PATH", "")},
            clear=False,
        ):
            environment = run_quality._minimal_environment(self.root)
        self.assertNotIn("OPENAI_API_KEY", environment)
        self.assertNotIn("sk-parent-secret", environment.values())

    def test_snapshot_detects_add_delete_rewrite_and_does_not_restore(self) -> None:
        def perform(action):
            def child(root, argv, timeout, output):
                action()
                return run_quality.ChildOutcome(0)

            return run_quality.execute_check(
                self.root,
                self.matrix,
                self.check,
                None,
                child_runner=child,
                prerequisite_available=lambda name: True,
            )

        result, stop = perform(lambda: (self.root / "added.txt").write_text("new", encoding="utf-8"))
        self.assertEqual("error", result.status)
        self.assertTrue(stop)
        self.assertTrue((self.root / "added.txt").exists())
        (self.root / "added.txt").unlink()

        result, stop = perform(lambda: (self.root / "source.txt").unlink())
        self.assertEqual("error", result.status)
        self.assertTrue(stop)
        self.assertFalse((self.root / "source.txt").exists())
        (self.root / "source.txt").write_text("original\n", encoding="utf-8")

        result, _ = perform(lambda: (self.root / "source.txt").write_text("changed\n", encoding="utf-8"))
        self.assertEqual("error", result.status)
        self.assertEqual("changed\n", (self.root / "source.txt").read_text(encoding="utf-8"))

    def test_mutation_stops_later_selected_checks(self) -> None:
        second = run_quality.Check(
            "second", "parity", 2, 4096, (), "Second fixture evidence."
        )
        matrix = run_quality.Matrix(
            checks=(self.check, second),
            profiles={"core": ("fixture", "second")},
            hard_timeout_seconds=10,
            hard_output_limit_bytes=65536,
            snapshot_limit_bytes=1048576,
            evidence_scope="Fixture.",
            human_review_boundary="Human pending.",
        )
        calls = 0

        def child(root, argv, timeout, output):
            nonlocal calls
            calls += 1
            (root / "mutation.txt").write_text("changed", encoding="utf-8")
            return run_quality.ChildOutcome(0)

        report = run_quality.run_quality(
            self.root,
            matrix,
            "core",
            matrix.profiles["core"],
            None,
            child_runner=child,
            prerequisite_available=lambda name: True,
        )
        self.assertEqual(1, calls)
        self.assertEqual(["error", "error"], [item.status for item in report.results])
        self.assertEqual(2, report.exit_code)

    def test_failure_continues_and_infrastructure_error_dominates(self) -> None:
        second = run_quality.Check(
            "second", "parity", 2, 4096, (), "Second fixture evidence."
        )
        matrix = run_quality.Matrix(
            checks=(self.check, second),
            profiles={"core": ("fixture", "second")},
            hard_timeout_seconds=10,
            hard_output_limit_bytes=65536,
            snapshot_limit_bytes=1048576,
            evidence_scope="Fixture.",
            human_review_boundary="Human pending.",
        )
        outcomes = iter((run_quality.ChildOutcome(1), run_quality.ChildOutcome(0)))
        report = run_quality.run_quality(
            self.root,
            matrix,
            "core",
            matrix.profiles["core"],
            None,
            child_runner=lambda *args: next(outcomes),
            prerequisite_available=lambda name: True,
        )
        self.assertEqual(["fail", "pass"], [item.status for item in report.results])
        self.assertEqual(1, report.exit_code)

        outcomes = iter((run_quality.ChildOutcome(None, "crash"), run_quality.ChildOutcome(1)))
        report = run_quality.run_quality(
            self.root,
            matrix,
            "core",
            matrix.profiles["core"],
            None,
            child_runner=lambda *args: next(outcomes),
            prerequisite_available=lambda name: True,
        )
        self.assertEqual(["error", "fail"], [item.status for item in report.results])
        self.assertEqual(2, report.exit_code)

    def test_missing_prerequisite_and_platform_are_unsupported_then_recover(self) -> None:
        check = run_quality.Check(
            "fixture", "curriculum", 2, 4096, ("fixture-tool",), "Fixture."
        )
        matrix = run_quality.Matrix(
            checks=(check,),
            profiles={"core": ("fixture",)},
            hard_timeout_seconds=10,
            hard_output_limit_bytes=65536,
            snapshot_limit_bytes=1048576,
            evidence_scope="Fixture.",
            human_review_boundary="Human pending.",
        )
        result, _ = run_quality.execute_check(
            self.root,
            matrix,
            check,
            None,
            child_runner=lambda *args: run_quality.ChildOutcome(0),
            prerequisite_available=lambda name: False,
        )
        self.assertEqual("unsupported", result.status)

        result, _ = run_quality.execute_check(
            self.root,
            matrix,
            check,
            None,
            child_runner=lambda *args: run_quality.ChildOutcome(0),
            prerequisite_available=lambda name: True,
        )
        self.assertEqual("pass", result.status)

        with mock.patch.object(run_quality, "process_tree_supported", return_value=False):
            result, _ = run_quality.execute_check(
                self.root,
                matrix,
                check,
                None,
                child_runner=lambda *args: self.fail("child must not run"),
                prerequisite_available=lambda name: True,
            )
        self.assertEqual("unsupported", result.status)

    def test_missing_prctl_symbol_is_reported_as_unsupported(self) -> None:
        with mock.patch.object(
            run_quality, "_get_child_subreaper", side_effect=AttributeError("prctl")
        ):
            self.assertFalse(run_quality.process_tree_supported())
            result, _ = run_quality.execute_check(
                self.root,
                self.matrix,
                self.check,
                None,
                child_runner=lambda *args: self.fail("child must not run"),
                prerequisite_available=lambda name: True,
            )
        self.assertEqual("unsupported", result.status)

    @unittest.skipUnless(run_quality.process_tree_supported(), "requires Linux subreaper containment")
    def test_subreaper_restore_failure_overrides_pass_and_aggregates_to_exit_two(self) -> None:
        with (
            mock.patch.object(run_quality, "process_tree_supported", return_value=True),
            mock.patch.object(run_quality, "_get_child_subreaper", return_value=0),
            mock.patch.object(
                run_quality,
                "_set_child_subreaper",
                side_effect=(None, OSError("restore failed")),
            ),
        ):
            outcome = run_quality.run_child(
                self.root, [sys.executable, "-c", "raise SystemExit(0)"], 2, 1024
            )
        self.assertIsNone(outcome.returncode)
        self.assertIn("restoration", outcome.infrastructure_error or "")

        report = run_quality.run_quality(
            self.root,
            self.matrix,
            "core",
            ("fixture",),
            None,
            child_runner=lambda *args: outcome,
            prerequisite_available=lambda name: True,
        )
        self.assertEqual("error", report.results[0].status)
        self.assertEqual(2, report.exit_code)

    def test_snapshot_is_bounded_and_includes_untracked_files(self) -> None:
        (self.root / "untracked.bin").write_bytes(b"x" * 32)
        (self.root / "empty.txt").touch()
        (self.root / "empty-directory").mkdir()
        (self.root / ".git").mkdir()
        (self.root / ".git" / "private-state").write_text("ignored", encoding="utf-8")
        snapshot = run_quality.snapshot_repository(self.root, 1024)
        self.assertIn("untracked.bin", snapshot)
        self.assertIn("empty.txt", snapshot)
        self.assertTrue(snapshot["empty.txt"].startswith("file:"))
        self.assertFalse(any(path.startswith(".git/") for path in snapshot))
        self.assertNotIn("empty-directory", snapshot)
        with self.assertRaisesRegex(run_quality.RunnerError, "exceeds"):
            run_quality.snapshot_repository(self.root, 4)


class ReportTests(unittest.TestCase):
    def report(self) -> object:
        results = tuple(
            run_quality.Result(
                id=f"check-{index}",
                adapter="fixture",
                status=status,
                evidence_scope="Observed fixture only.",
                message="Ruta segura: capítol/README.ca.md",
            )
            for index, status in enumerate(
                ("pass", "fail", "error", "unsupported", "not-selected"), start=1
            )
        )
        return run_quality.Report(
            evidence_scope="Automated evidence only.",
            human_review_boundary="Linguistic, pedagogical, accessibility, bidi, and provenance gates remain human.",
            selection="fixture",
            selected_checks=("check-1", "check-2", "check-3", "check-4"),
            changed_from=None,
            revision="a" * 40,
            repository_tree_sha256="b" * 64,
            observed_host={
                "python": "3.11.0",
                "operating_system": "FixtureOS",
                "architecture": "fixture",
                "scope": "observed host only",
            },
            results=results,
        )

    def test_json_and_markdown_are_byte_stable_ordered_and_accessible(self) -> None:
        report = self.report()
        first_json = run_quality.render_json(report)
        first_markdown = run_quality.render_markdown(report)
        self.assertEqual(first_json, run_quality.render_json(report))
        self.assertEqual(first_markdown, run_quality.render_markdown(report))
        payload = json.loads(first_json)
        self.assertEqual(1, payload["schema_version"])
        self.assertEqual(
            ["pass", "fail", "error", "unsupported", "not-selected"],
            [item["status"] for item in payload["results"]],
        )
        self.assertIn("capítol", first_json)
        self.assertIn("| Check | Status | Evidence scope | Result |", first_markdown)
        for status in ("pass", "fail", "error", "unsupported", "not-selected"):
            self.assertIn(status, first_markdown)
        self.assertIn("Human review boundary", first_markdown)
        for volatile in ("timestamp", "duration", str(Path.home()), "/tmp/"):
            self.assertNotIn(volatile, first_json)
            self.assertNotIn(volatile, first_markdown)

    def test_text_is_projection_of_same_status_model(self) -> None:
        rendered = run_quality.render_text(self.report())
        self.assertIn("Quality evidence: error", rendered)
        self.assertIn("PASS check-1", rendered)
        self.assertIn("NOT-SELECTED check-5", rendered)
        self.assertIn("Human review boundary", rendered)

    def test_sensitive_and_absolute_failure_details_are_redacted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="quality-redaction-") as temporary:
            root = Path(temporary)
            message = (
                f"token=super-secret-value at {root}/private.txt "
                f"and {Path.home()}/learner.txt"
            )
            safe = run_quality.sanitize_message(message, root)
            self.assertNotIn("super-secret-value", safe)
            self.assertNotIn(str(root), safe)
            self.assertNotIn(str(Path.home()), safe)
            self.assertIn("<redacted>", safe)

    def test_windows_drive_and_unc_paths_are_redacted(self) -> None:
        message = (
            r"failed at C:\Users\Learner\private\file.txt, "
            r"\\server\share\student\notes.txt, and //server/share/other.txt"
        )
        safe = run_quality.sanitize_message(message, ROOT)
        self.assertNotIn("C:\\Users", safe)
        self.assertNotIn("\\\\server", safe)
        self.assertNotIn("//server", safe)
        self.assertGreaterEqual(safe.count("<path>"), 3)

    def test_spaced_paths_ansi_and_openai_key_never_reach_public_results(self) -> None:
        message = (
            "\x1b[31mOPENAI_API_KEY=sk-fixture-secret-value\x1b[0m "
            "at /tmp/My Project/private notes.txt, "
            r"C:\Program Files\Private Course\notes.txt, "
            r"\\server\Shared Folder\Private Course\notes.txt"
        )
        result = run_quality.Result(
            "fixture", "fixture", "error", "Observed fixture only.", message
        )
        for leaked in (
            "\x1b",
            "sk-fixture-secret-value",
            "My Project",
            "Program Files",
            "Shared Folder",
            "OPENAI_API_KEY",
        ):
            self.assertNotIn(leaked, result.message)
        self.assertIn("<redacted>", result.message)
        self.assertGreaterEqual(result.message.count("<path>"), 3)

    def test_direct_public_contract_objects_reject_unsafe_boundaries(self) -> None:
        with self.assertRaisesRegex(ValueError, "safe public text"):
            run_quality.Result(
                "fixture",
                "fixture",
                "error",
                "OPENAI_API_KEY=sk-fixture-secret",
                "safe message",
            )
        with self.assertRaisesRegex(ValueError, "safe text"):
            run_quality.Report(
                evidence_scope="Automated evidence only.",
                human_review_boundary="Review /tmp/Private Course/notes.txt",
                selection="fixture",
                selected_checks=(),
                changed_from=None,
                revision="unavailable",
                repository_tree_sha256="b" * 64,
                observed_host={},
                results=(),
            )

    def test_fatal_json_is_schema_valid_and_contains_no_traceback(self) -> None:
        rendered = run_quality.render_fatal("json", "bad matrix", ROOT)
        payload = json.loads(rendered)
        self.assertEqual("error", payload["overall_status"])
        self.assertEqual("runner.config", payload["diagnostics"][0]["id"])
        self.assertNotIn("Traceback", rendered)


if __name__ == "__main__":
    unittest.main()
