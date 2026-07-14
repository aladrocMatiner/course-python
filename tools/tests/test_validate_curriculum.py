from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import validate_curriculum  # noqa: E402


class CurriculumValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ("a", "b", "c"):
            unit = self.root / name
            unit.mkdir()
            (unit / "README.md").write_text(f"# {name.upper()}\n\n## Checkpoint\n", encoding="utf-8")
        self.contract = {
            "schema_version": 1,
            "metadata": {"evidence_scope": "Declared dependencies only; human review remains required."},
            "concept": [
                {"id": "alpha", "introduced_by": "a"},
                {"id": "beta", "introduced_by": "b"},
                {"id": "gamma", "introduced_by": "c"},
            ],
            "checkpoint": [
                {"id": "a", "order": 1, "path": "a/README.md", "anchor": "checkpoint", "prerequisites": [], "requires": [], "teaches": ["alpha"]},
                {"id": "b", "order": 2, "path": "b/README.md", "anchor": "checkpoint", "prerequisites": ["a"], "requires": ["alpha"], "teaches": ["beta"]},
                {"id": "c", "order": 3, "path": "c/README.md", "anchor": "checkpoint", "prerequisites": ["b"], "requires": ["beta"], "teaches": ["gamma"]},
            ],
            "route": [{"id": "route", "title": "Route", "duration": "3 sessions", "outcome": "Observable result", "completion": "Pass checkpoint C", "stopping_point": "Stop after any checkpoint", "entry_checkpoints": [], "checkpoints": ["a", "b", "c"]}],
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def codes(self, contract: dict | None = None) -> set[str]:
        return {issue.code for issue in validate_curriculum.validate_contract(self.root, contract or self.contract)}

    def test_valid_contract_passes(self) -> None:
        self.assertEqual(set(), self.codes())

    def test_missing_path_fails_safely(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["checkpoint"][1]["path"] = "missing/README.md"
        self.assertIn("CURRICULUM_MISSING_PATH", self.codes(contract))

    def test_missing_anchor_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["checkpoint"][1]["anchor"] = "does-not-exist"
        self.assertIn("CURRICULUM_MISSING_ANCHOR", self.codes(contract))

    def test_unknown_concept_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["checkpoint"][1]["requires"] = ["unknown"]
        self.assertIn("CURRICULUM_UNKNOWN_CONCEPT", self.codes(contract))

    def test_forward_required_concept_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["checkpoint"][1]["requires"] = ["gamma"]
        self.assertIn("CURRICULUM_FORWARD_CONCEPT", self.codes(contract))

    def test_forward_checkpoint_dependency_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["checkpoint"][0]["prerequisites"] = ["b"]
        self.assertIn("CURRICULUM_FORWARD_DEPENDENCY", self.codes(contract))

    def test_unknown_checkpoint_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["checkpoint"][1]["prerequisites"] = ["missing"]
        self.assertIn("CURRICULUM_UNKNOWN_CHECKPOINT", self.codes(contract))

    def test_path_escape_fails_safely(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["checkpoint"][1]["path"] = "../outside.md"
        self.assertIn("CURRICULUM_PATH_ESCAPE", self.codes(contract))

    def test_cycle_fails_with_bounded_relative_diagnostic(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["checkpoint"][0]["prerequisites"] = ["c"]
        issues = validate_curriculum.validate_contract(self.root, contract)
        self.assertIn("CURRICULUM_CYCLE", {issue.code for issue in issues})
        rendered = "\n".join(f"{issue.path} {issue.message}" for issue in issues)
        self.assertNotIn(str(self.root), rendered)

    def test_json_cli_reports_declared_evidence_only(self) -> None:
        map_path = ROOT / "tools" / "curriculum_map.toml"
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / "tools" / "validate_curriculum.py"), "--repo-root", str(ROOT), "--map", str(map_path), "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("declared-contract-only", payload["evidence_scope"])
        self.assertEqual("pass", payload["status"])


if __name__ == "__main__":
    unittest.main()
