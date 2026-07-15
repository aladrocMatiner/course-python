from __future__ import annotations

import base64
import csv
import hashlib
import importlib.util
import io
import os
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
VERIFIER = PROJECT / "tools" / "verify_artifact.py"

SPEC = importlib.util.spec_from_file_location("order_tracker_artifact_verifier", VERIFIER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("artifact verifier could not be loaded")
ARTIFACT_VERIFIER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ARTIFACT_VERIFIER
SPEC.loader.exec_module(ARTIFACT_VERIFIER)

METADATA = b"""Metadata-Version: 2.4
Name: course-order-tracker
Version: 1.0.0
License-Expression: CC-BY-SA-4.0
License-File: LICENSE
Requires-Python: >=3.11
Description-Content-Type: text/markdown

# `course-order-tracker` companion project
"""
ENTRY_POINTS = b"[console_scripts]\norder-tracker = order_tracker.cli:run\n"
PACKAGE_FILES = {
    f"order_tracker/{name}.py": b"# synthetic inspection fixture\n"
    for name in (
        "__init__",
        "__main__",
        "cli",
        "domain",
        "loopback",
        "repositories",
        "service",
    )
}


def wheel_members(*, unexpected: bool = False) -> dict[str, bytes]:
    dist_info = "course_order_tracker-1.0.0.dist-info"
    members = {
        **PACKAGE_FILES,
        f"{dist_info}/METADATA": METADATA,
        f"{dist_info}/WHEEL": (
            b"Wheel-Version: 1.0\nGenerator: test fixture\n"
            b"Root-Is-Purelib: true\nTag: py3-none-any\n"
        ),
        f"{dist_info}/entry_points.txt": ENTRY_POINTS,
        f"{dist_info}/licenses/LICENSE": b"Original example under CC BY-SA 4.0.\n",
        f"{dist_info}/top_level.txt": b"order_tracker\n",
    }
    if unexpected:
        members["order_tracker/test_network_hook.py"] = b"# must not ship\n"
    record_name = f"{dist_info}/RECORD"
    record = io.StringIO(newline="")
    writer = csv.writer(record)
    for name, content in members.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=")
        writer.writerow((name, f"sha256={digest.decode()}", str(len(content))))
    writer.writerow((record_name, "", ""))
    members[record_name] = record.getvalue().encode("utf-8")
    return members


def write_wheel(path: Path, *, unexpected: bool = False) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in wheel_members(unexpected=unexpected).items():
            archive.writestr(name, content)


def sdist_members(*, unexpected: bool = False) -> dict[str, bytes]:
    egg_info = "src/course_order_tracker.egg-info"
    package_files = {
        f"src/{name}": content for name, content in PACKAGE_FILES.items()
    }
    members = {
        "BUILD_INPUTS.md": b"# Artifact-verification build-input record\n",
        "LICENSE": b"Original example under CC BY-SA 4.0.\n",
        "MANIFEST.in": b"recursive-include src/order_tracker *.py\n",
        "PKG-INFO": METADATA,
        "README.md": b"# `course-order-tracker` companion project\n",
        "pyproject.toml": b"[build-system]\n",
        "requirements-build.txt": b"build==1.3.0\n",
        "setup.cfg": b"[egg_info]\ntag_build =\n",
        f"{egg_info}/PKG-INFO": METADATA,
        f"{egg_info}/SOURCES.txt": b"README.md\n",
        f"{egg_info}/dependency_links.txt": b"\n",
        f"{egg_info}/entry_points.txt": ENTRY_POINTS,
        f"{egg_info}/top_level.txt": b"order_tracker\n",
        **package_files,
    }
    if unexpected:
        members["src/order_tracker/test_network_hook.py"] = b"# must not ship\n"
    return members


def write_sdist(path: Path, *, unexpected: bool = False) -> None:
    root = "course_order_tracker-1.0.0"
    with tarfile.open(path, "w:gz") as archive:
        for relative, content in sdist_members(unexpected=unexpected).items():
            info = tarfile.TarInfo(f"{root}/{relative}")
            info.size = len(content)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(content))


def source_snapshot() -> dict[str, bytes]:
    return {
        path.relative_to(PROJECT).as_posix(): path.read_bytes()
        for path in sorted(PROJECT.rglob("*"))
        if path.is_file()
    }


class ArtifactVerifierTests(unittest.TestCase):
    def test_wheel_metadata_ignores_vendored_distribution_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            wheel = Path(directory) / "setuptools-80.9.0-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr(
                    "setuptools-80.9.0.dist-info/METADATA",
                    "Name: setuptools\nVersion: 80.9.0\n\n",
                )
                archive.writestr(
                    "setuptools/_vendor/example-1.0.dist-info/METADATA",
                    "Name: example\nVersion: 1.0\n\n",
                )

            self.assertEqual(
                ("setuptools", "80.9.0"),
                ARTIFACT_VERIFIER.wheel_metadata(wheel),
            )

    def test_bounded_child_capture_accepts_small_output_and_rejects_overflow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment = os.environ.copy()
            small = ARTIFACT_VERIFIER.bounded_run(
                [sys.executable, "-I", "-B", "-c", "print('bounded')"],
                phase="synthetic bounded output",
                cwd=root,
                environment=environment,
                timeout=2,
            )
            self.assertEqual(small.stdout, "bounded\n")
            with self.assertRaises(ARTIFACT_VERIFIER.VerificationFailure) as raised:
                ARTIFACT_VERIFIER.bounded_run(
                    [
                        sys.executable,
                        "-I",
                        "-B",
                        "-c",
                        "import os; os.write(1, b'x' * 20000)",
                    ],
                    phase="synthetic oversized output",
                    cwd=root,
                    environment=environment,
                    timeout=2,
                )
            self.assertIn("output exceeded", str(raised.exception))

    def test_bounded_child_timeout_terminates_promptly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            started = time.monotonic()
            with self.assertRaises(ARTIFACT_VERIFIER.VerificationFailure) as raised:
                ARTIFACT_VERIFIER.bounded_run(
                    [sys.executable, "-I", "-B", "-c", "import time; time.sleep(10)"],
                    phase="synthetic timeout",
                    cwd=Path(directory),
                    environment=os.environ.copy(),
                    timeout=0.05,
                )
            self.assertLess(time.monotonic() - started, 1)
            self.assertIn("exceeded the 0.05-second bound", str(raised.exception))

    def test_missing_explicit_prerequisite_stops_without_acquisition_or_residue(self) -> None:
        before = source_snapshot()
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment.pop("ORDER_TRACKER_WHEELHOUSE", None)
        with tempfile.TemporaryDirectory() as directory:
            foreign = Path(directory)
            result = subprocess.run(
                [sys.executable, "-B", VERIFIER],
                cwd=foreign,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
                check=False,
            )
            self.assertEqual(list(foreign.iterdir()), [])
        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.startswith("prerequisite missing:"), result.stderr)
        self.assertNotIn("installing", result.stderr.lower())
        self.assertEqual(source_snapshot(), before)

    def test_wheelhouse_rejects_forged_hash_without_using_an_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            wheelhouse = Path(directory)
            for filename, name, version in (
                ("setuptools-80.9.0-py3-none-any.whl", "setuptools", "80.9.0"),
                ("wheel-0.45.1-py3-none-any.whl", "wheel", "0.45.1"),
            ):
                with zipfile.ZipFile(wheelhouse / filename, "w") as archive:
                    archive.writestr(
                        f"{name}-{version}.dist-info/METADATA",
                        f"Name: {name}\nVersion: {version}\n\n",
                    )
            with (
                patch.object(
                    ARTIFACT_VERIFIER.importlib.metadata,
                    "version",
                    return_value="1.3.0",
                ),
                patch.dict(
                    os.environ,
                    {"ORDER_TRACKER_WHEELHOUSE": str(wheelhouse)},
                    clear=False,
                ),
                self.assertRaises(ARTIFACT_VERIFIER.PrerequisiteMissing) as raised,
            ):
                ARTIFACT_VERIFIER.require_prerequisites()
            self.assertIn("do not match recorded metadata/SHA-256", str(raised.exception))

    def test_wheel_inspection_accepts_declared_members_and_rejects_hook(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "course_order_tracker-1.0.0-py3-none-any.whl"
            unexpected = root / "unexpected" / valid.name
            unexpected.parent.mkdir()
            write_wheel(valid)
            write_wheel(unexpected, unexpected=True)
            ARTIFACT_VERIFIER.inspect_wheel(valid)
            with self.assertRaises(ARTIFACT_VERIFIER.VerificationFailure) as raised:
                ARTIFACT_VERIFIER.inspect_wheel(unexpected)
            self.assertIn("undeclared members", str(raised.exception))

    def test_sdist_inspection_accepts_declared_members_and_rejects_hook(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "course_order_tracker-1.0.0.tar.gz"
            unexpected = root / "unexpected" / valid.name
            unexpected.parent.mkdir()
            write_sdist(valid)
            write_sdist(unexpected, unexpected=True)
            ARTIFACT_VERIFIER.inspect_sdist(valid)
            with self.assertRaises(ARTIFACT_VERIFIER.VerificationFailure) as raised:
                ARTIFACT_VERIFIER.inspect_sdist(unexpected)
            self.assertIn("undeclared members", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
