from __future__ import annotations

import importlib.util
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Iterator
from unittest import mock


MODULE_PATH = Path(__file__).with_name("bookcheck_plugin.py")
SPEC = importlib.util.spec_from_file_location("patterns_bookcheck_plugin", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@contextmanager
def suite_fixture(filename: str) -> Iterator[str]:
    with tempfile.TemporaryDirectory() as raw_temp:
        filenames = [filename]
        if filename == "test_core_patterns.py":
            filenames.append("test_core_catalog.py")
        for required in filenames:
            test_file = Path(raw_temp) / MODULE.TEST_DIRECTORY / required
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("# synthetic selection fixture\n", encoding="utf-8")
        yield raw_temp


class Registry:
    def __init__(self) -> None:
        self.options: dict[str, object] = {}

    def add(self, **options: object) -> None:
        self.options = options


class PatternsPluginTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = Registry()
        MODULE.register(self.registry)

    def test_registration_contract_is_exact(self) -> None:
        self.assertEqual("patterns", self.registry.options["plugin_id"])
        self.assertEqual(1, self.registry.options["api_version"])
        self.assertEqual((), self.registry.options["prerequisites"])
        self.assertEqual(30, self.registry.options["timeout"])
        self.assertEqual(
            {"core-suite", "network-suite"},
            set(self.registry.options["checks"]),
        )

    def test_selecting_core_does_not_execute_network(self) -> None:
        checks = self.registry.options["checks"]
        assert isinstance(checks, dict)
        with suite_fixture("test_core_patterns.py") as root, mock.patch.object(
            MODULE.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=0),
        ) as run:
            findings = checks["core-suite"]({"root": root})
        self.assertEqual([], findings)
        command = run.call_args.args[0]
        self.assertIn("test_core*.py", command)
        self.assertNotIn("test_network_patterns.py", command)

    def test_missing_catalog_contract_does_not_start_core_process(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            test_file = Path(raw_temp) / MODULE.TEST_DIRECTORY / "test_core_patterns.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("# core fixture\n", encoding="utf-8")
            with mock.patch.object(MODULE.subprocess, "run") as run:
                findings = MODULE.check_core_suite({"root": raw_temp})
        run.assert_not_called()
        self.assertEqual("missing-suite", findings[0]["rule_id"])
        self.assertTrue(findings[0]["path"].endswith("test_core_catalog.py"))

    def test_selecting_network_does_not_execute_core(self) -> None:
        checks = self.registry.options["checks"]
        assert isinstance(checks, dict)
        with suite_fixture("test_network_patterns.py") as root, mock.patch.object(
            MODULE.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=0),
        ) as run:
            findings = checks["network-suite"]({"root": root})
        self.assertEqual([], findings)
        command = run.call_args.args[0]
        self.assertIn("test_network_patterns.py", command)
        self.assertNotIn("test_core_patterns.py", command)

    def test_failure_is_one_bounded_repository_relative_finding(self) -> None:
        with suite_fixture("test_core_patterns.py") as root, mock.patch.object(
            MODULE.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=7),
        ):
            findings = MODULE.check_core_suite({"root": root})
        self.assertEqual(1, len(findings))
        self.assertEqual("failure", findings[0]["rule_id"])
        self.assertEqual("return-code:7:core-suite", findings[0]["construct"])
        self.assertFalse(Path(findings[0]["path"]).is_absolute())

    def test_missing_suite_does_not_start_a_process(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp, mock.patch.object(
            MODULE.subprocess, "run"
        ) as run:
            findings = MODULE.check_network_suite({"root": raw_temp})
        run.assert_not_called()
        self.assertEqual("missing-suite", findings[0]["rule_id"])
        self.assertNotIn(raw_temp, str(findings))

    def test_symlinked_test_directory_is_rejected_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            base = Path(raw_temp)
            root = base / "repository"
            external = base / "external-tests"
            external.mkdir()
            (external / "test_core_patterns.py").write_text(
                "raise RuntimeError('must not execute')\n", encoding="utf-8"
            )
            tests_link = root / "zz_Appendix C Software Design Patterns/tests"
            tests_link.parent.mkdir(parents=True)
            try:
                tests_link.symlink_to(external, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symbolic links are unavailable: {error}")

            with mock.patch.object(MODULE.subprocess, "run") as run:
                findings = MODULE.check_core_suite({"root": str(root)})

        run.assert_not_called()
        self.assertEqual(1, len(findings))
        self.assertEqual("unsafe-suite-path", findings[0]["rule_id"])
        self.assertNotIn(str(external), str(findings))

    def test_os_error_is_reported_without_host_details(self) -> None:
        with suite_fixture("test_core_patterns.py") as root, mock.patch.object(
            MODULE.subprocess,
            "run",
            side_effect=OSError("sensitive host detail"),
        ):
            findings = MODULE.check_core_suite({"root": root})
        self.assertEqual("runner-error", findings[0]["rule_id"])
        self.assertNotIn("sensitive host detail", str(findings))


if __name__ == "__main__":
    unittest.main()
