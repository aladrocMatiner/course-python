from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

PLUGIN = Path(__file__).with_name("bookcheck_plugin.py")
SPEC = importlib.util.spec_from_file_location("chapter23_plugin", PLUGIN)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Registry:
    def __init__(self) -> None:
        self.options: dict[str, object] = {}

    def add(self, **options: object) -> None:
        self.options = options


class PluginTests(unittest.TestCase):
    def test_registration_contract(self) -> None:
        registry = Registry()
        MODULE.register(registry)
        self.assertEqual(registry.options["plugin_id"], "network")
        self.assertEqual(registry.options["api_version"], 1)
        self.assertEqual(set(registry.options["checks"]), {"network-suite"})


if __name__ == "__main__":
    unittest.main()
