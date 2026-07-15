from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "src"


class CLITests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.foreign = Path(self.temporary.name) / "foreign"
        self.foreign.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(
        self,
        *arguments: str,
        extra_environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SOURCE)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment.pop("ORDER_TRACKER_DB", None)
        if extra_environment:
            environment.update(extra_environment)
        result = subprocess.run(
            [sys.executable, "-B", "-m", "order_tracker", *arguments],
            cwd=self.foreign,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertLessEqual(len(result.stdout) + len(result.stderr), 8_192)
        return result

    def test_missing_configuration_exits_two_without_creating_state(self) -> None:
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(
            result.stderr,
            "error: database path required; use --database PATH or ORDER_TRACKER_DB\n",
        )
        self.assertEqual(list(self.foreign.iterdir()), [])

    def test_add_list_and_advance_have_stable_json_output(self) -> None:
        database = self.foreign / "orders.sqlite3"
        added = self.run_cli("--database", str(database), "add", "ORD-001", "widget", "2")
        listed = self.run_cli("--database", str(database), "list")
        advanced = self.run_cli("--database", str(database), "advance", "ORD-001")

        self.assertEqual(added.returncode, 0)
        self.assertEqual(added.stdout, '{"order_id":"ORD-001","status":"pending"}\n')
        self.assertEqual(
            listed.stdout,
            '{"item":"widget","order_id":"ORD-001","quantity":2,"status":"pending"}\n',
        )
        self.assertEqual(advanced.stdout, '{"order_id":"ORD-001","status":"packed"}\n')
        self.assertEqual(added.stderr + listed.stderr + advanced.stderr, "")

    def test_explicit_database_overrides_environment_without_touching_it(self) -> None:
        environment_database = self.foreign / "environment.sqlite3"
        explicit_database = self.foreign / "explicit.sqlite3"
        result = self.run_cli(
            "--database",
            str(explicit_database),
            "add",
            "ORD-001",
            "widget",
            "2",
            extra_environment={"ORDER_TRACKER_DB": str(environment_database)},
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(explicit_database.exists())
        self.assertFalse(environment_database.exists())

    def test_environment_database_is_used_when_flag_is_absent(self) -> None:
        database = self.foreign / "environment.sqlite3"
        result = self.run_cli(
            "add",
            "ORD-ENV",
            "widget",
            "2",
            extra_environment={"ORDER_TRACKER_DB": str(database)},
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '{"order_id":"ORD-ENV","status":"pending"}\n')
        self.assertTrue(database.exists())

    def test_invalid_quantity_and_duplicate_recover_without_partial_insert(self) -> None:
        database = self.foreign / "orders.sqlite3"
        non_integer = self.run_cli(
            "--database", str(database), "add", "ORD-001", "widget", "two"
        )
        self.assertEqual(non_integer.returncode, 2)
        self.assertFalse(database.exists())

        zero = self.run_cli("--database", str(database), "add", "ORD-001", "widget", "0")
        self.assertEqual(zero.returncode, 1)
        self.assertIn("error[validation-error]", zero.stderr)

        too_large = self.run_cli(
            "--database", str(database), "add", "ORD-001", "widget", "1001"
        )
        self.assertEqual(too_large.returncode, 1)
        self.assertIn("error[validation-error]", too_large.stderr)

        created = self.run_cli("--database", str(database), "add", "ORD-001", "widget", "2")
        duplicate = self.run_cli(
            "--database", str(database), "add", "ORD-001", "replacement", "9"
        )
        listed = self.run_cli("--database", str(database), "list")
        self.assertEqual(created.returncode, 0)
        self.assertEqual(duplicate.returncode, 1)
        self.assertIn("error[duplicate-order]", duplicate.stderr)
        self.assertNotIn("Traceback", duplicate.stderr)
        self.assertEqual(json.loads(listed.stdout)["item"], "widget")

    def test_verbose_logs_exclude_item_paths_and_environment_values(self) -> None:
        database = self.foreign / "very-private-location.sqlite3"
        result = self.run_cli(
            "--verbose",
            "--database",
            str(database),
            "add",
            "ORD-LOG",
            "secret-item-text",
            "1",
            extra_environment={"ORDER_TRACKER_DB": "hidden-environment-value"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "event=add order_id=ORD-LOG outcome=success\n")
        combined = result.stdout + result.stderr
        self.assertNotIn("secret-item-text", combined)
        self.assertNotIn(str(database), combined)
        self.assertNotIn("hidden-environment-value", combined)

    def test_verbose_expected_error_uses_stable_safe_category(self) -> None:
        database = self.foreign / "private-location.sqlite3"
        self.run_cli(
            "--database", str(database), "add", "ORD-LOG", "first-secret-item", "1"
        )
        result = self.run_cli(
            "--verbose",
            "--database",
            str(database),
            "add",
            "ORD-LOG",
            "second-secret-item",
            "9",
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr,
            "event=add order_id=ORD-LOG outcome=error category=duplicate-order\n"
            "error[duplicate-order]: order ORD-LOG already exists\n",
        )
        self.assertNotIn("secret-item", result.stderr)
        self.assertNotIn(str(database), result.stderr)

    def test_repository_error_has_phase_without_path_or_traceback(self) -> None:
        database = self.foreign / "broken.sqlite3"
        database.write_bytes(b"broken")
        result = self.run_cli("--verbose", "--database", str(database), "list")
        self.assertEqual(result.returncode, 1)
        self.assertIn("database initialization failed", result.stderr)
        self.assertIn("category=repository-error", result.stderr)
        self.assertNotIn(str(database), result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
