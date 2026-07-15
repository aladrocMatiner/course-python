from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "src"


class MetadataTests(unittest.TestCase):
    def test_project_metadata_declares_pure_standard_library_contract(self) -> None:
        with (PROJECT / "pyproject.toml").open("rb") as stream:
            configuration = tomllib.load(stream)
        project = configuration["project"]
        self.assertEqual(project["name"], "course-order-tracker")
        self.assertEqual(project["version"], "1.0.0")
        self.assertEqual(project["requires-python"], ">=3.11")
        self.assertEqual(project["readme"], "README.md")
        self.assertEqual(project["license"], "CC-BY-SA-4.0")
        self.assertEqual(project["license-files"], ["LICENSE"])
        self.assertEqual(project["dependencies"], [])
        self.assertEqual(project["scripts"]["order-tracker"], "order_tracker.cli:run")
        self.assertEqual(
            configuration["build-system"]["requires"],
            ["setuptools==80.9.0", "wheel==0.45.1"],
        )
        self.assertEqual(configuration["build-system"]["build-backend"], "setuptools.build_meta")
        self.assertEqual(configuration["tool"]["setuptools"]["package-dir"], {"": "src"})

    def test_build_input_is_described_as_direct_pins_not_a_lock(self) -> None:
        text = (PROJECT / "requirements-build.txt").read_text(encoding="utf-8")
        self.assertIn("not a resolver-generated", text)
        self.assertIn("build==1.3.0", text)
        self.assertIn("setuptools==80.9.0", text)
        self.assertIn("wheel==0.45.1", text)
        provenance = (PROJECT / "BUILD_INPUTS.md").read_text(encoding="utf-8")
        self.assertIn("not a transitive dependency lock", provenance)
        for digest in (
            "7145f0b5061ba90a1500d60bd1b13ca0a8a4cebdd0cc16ed8adf1c0e739f43b4",
            "062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922",
            "708e7481cc80179af0e556bbf0cc00b8444c7321e2700b8d8580231d13017248",
        ):
            self.assertIn(digest, provenance)

    def test_clean_source_import_from_foreign_directory_has_no_side_effects(self) -> None:
        script = (
            "import json, pathlib, sys; "
            f"sys.path.insert(0, {str(SOURCE)!r}); "
            "import order_tracker; "
            "print(json.dumps({'version': order_tracker.__version__, "
            "'file': order_tracker.__file__}))"
        )
        with tempfile.TemporaryDirectory() as directory:
            foreign = Path(directory)
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-c", script],
                cwd=foreign,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = json.loads(result.stdout)
            self.assertEqual(evidence["version"], "1.0.0")
            self.assertTrue(Path(evidence["file"]).is_relative_to(SOURCE))
            self.assertEqual(list(foreign.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
