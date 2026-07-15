from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "tools" / "learning_bridges_plugin.py"
SPEC = importlib.util.spec_from_file_location("learning_bridges_plugin", PLUGIN)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Registry:
    def __init__(self) -> None:
        self.options: dict[str, object] = {}

    def add(self, **options: object) -> None:
        self.options = options


class LearningBridgesPluginTests(unittest.TestCase):
    def test_registration_contract(self) -> None:
        registry = Registry()
        MODULE.register(registry)

        self.assertEqual("learning", registry.options["plugin_id"])
        self.assertEqual(1, registry.options["api_version"])
        self.assertEqual({"contract"}, set(registry.options["checks"]))
        self.assertEqual((), registry.options["prerequisites"])

    def test_disposable_beginner_bridges_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="learning-bridge-test-") as raw_temp:
            findings = MODULE._early_bridge_contract(Path(raw_temp))

        self.assertEqual([], findings)

    def test_missing_companion_fails_closed_before_execution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="learning-bridge-root-") as raw_root:
            findings = MODULE.check_contract({"root": raw_root})

        self.assertGreater(len(findings), 1)
        self.assertTrue(all(item["rule_id"] == "missing-source" for item in findings))
        self.assertTrue(
            any("chapter-28-professional-capstone" in item["path"] for item in findings)
        )


if __name__ == "__main__":
    unittest.main()
