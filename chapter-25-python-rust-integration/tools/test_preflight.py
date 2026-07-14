from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("preflight.py")
SPEC = importlib.util.spec_from_file_location("chapter25_preflight", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


class CompilerSelectionTests(unittest.TestCase):
    def test_windows_prefers_msvc_developer_shell(self) -> None:
        with patch.object(
            preflight.shutil,
            "which",
            side_effect=lambda tool: "C:/BuildTools/cl.exe" if tool == "cl" else None,
        ):
            self.assertEqual(preflight.find_c_compiler("Windows"), "cl")

    def test_unix_prefers_cc_and_falls_back_to_clang(self) -> None:
        with patch.object(
            preflight.shutil,
            "which",
            side_effect=lambda tool: "/usr/bin/clang" if tool == "clang" else None,
        ):
            self.assertEqual(preflight.find_c_compiler("Linux"), "clang")

    def test_missing_compiler_is_explicit(self) -> None:
        with patch.object(preflight.shutil, "which", return_value=None):
            self.assertIsNone(preflight.find_c_compiler("Windows"))
            self.assertEqual(
                preflight.compiler_candidates("Windows"), ("cl", "clang-cl")
            )


if __name__ == "__main__":
    unittest.main()
