from __future__ import annotations

import base64
import contextlib
import csv
import hashlib
import importlib.util
import io
import os
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "verify_artifact.py"
SPEC = importlib.util.spec_from_file_location("verify_artifact", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
verify_artifact = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_artifact)


class WheelInspectionTests(unittest.TestCase):
    def make_wheel(
        self,
        *,
        leak_src: bool = False,
        extra_module: bool = False,
        missing_wheel_metadata: bool = False,
        wrong_name: bool = False,
        false_record: bool = False,
    ) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        wheel = Path(temporary.name) / verify_artifact.EXPECTED_WHEEL_NAME
        dist_info = verify_artifact.DIST_INFO
        package_files = sorted(verify_artifact.EXPECTED_PACKAGE_FILES)
        source_root = verify_artifact.PROJECT / "src"
        members = {name: (source_root / name).read_bytes() for name in package_files}
        members[f"{dist_info}/METADATA"] = (
            "Metadata-Version: 2.4\n"
            f"Name: {'not-course-mi-app' if wrong_name else 'course-mi-app'}\n"
            "Version: 0.1.0\n"
            "Requires-Python: >=3.11\n"
        ).encode()
        members[f"{dist_info}/entry_points.txt"] = (
            b"[console_scripts]\nmi-app = mi_app.cli:main\n"
        )
        if not missing_wheel_metadata:
            members[f"{dist_info}/WHEEL"] = (
                b"Wheel-Version: 1.0\n"
                b"Generator: fixture\n"
                b"Root-Is-Purelib: true\n"
                b"Tag: py3-none-any\n"
            )
        members[f"{dist_info}/top_level.txt"] = b"mi_app\n"
        if leak_src:
            members["src/mi_app/domain.py"] = b""
        if extra_module:
            members["mi_app/undeclared.py"] = b""

        record_buffer = io.StringIO(newline="")
        writer = csv.writer(record_buffer, lineterminator="\n")
        for name, content in sorted(members.items()):
            digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest())
            encoded_digest = digest.rstrip(b"=").decode()
            recorded_size = str(len(content))
            if false_record and name == "mi_app/domain.py":
                encoded_digest = base64.urlsafe_b64encode(b"x" * 32).rstrip(b"=").decode()
                recorded_size = "999999"
            writer.writerow(
                [name, f"sha256={encoded_digest}", recorded_size]
            )
        writer.writerow([f"{dist_info}/RECORD", "", ""])
        members[f"{dist_info}/RECORD"] = record_buffer.getvalue().encode()

        with zipfile.ZipFile(wheel, "w") as archive:
            for name, content in members.items():
                archive.writestr(name, content)
        return wheel

    def test_accepts_the_documented_artifact_contract(self) -> None:
        verify_artifact.inspect_wheel(self.make_wheel())

    def test_rejects_a_src_container_leak(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "source-layout container"):
            verify_artifact.inspect_wheel(self.make_wheel(leak_src=True))

    def test_rejects_an_extra_package_module(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "unexpected top-level"):
            verify_artifact.inspect_wheel(self.make_wheel(extra_module=True))

    def test_rejects_missing_wheel_metadata(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "missing metadata"):
            verify_artifact.inspect_wheel(
                self.make_wheel(missing_wheel_metadata=True)
            )

    def test_parses_metadata_instead_of_accepting_a_name_substring(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "name/version"):
            verify_artifact.inspect_wheel(self.make_wheel(wrong_name=True))

    def test_rejects_false_record_digest_and_size_evidence(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "RECORD digest"):
            verify_artifact.inspect_wheel(self.make_wheel(false_record=True))

    def make_build_requirement_wheel(
        self, directory: Path, distribution: str, version: str
    ) -> Path:
        normalized = distribution.replace("-", "_")
        wheel = directory / f"{normalized}-{version}-py3-none-any.whl"
        dist_info = f"{normalized}-{version}.dist-info"
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr(
                f"{dist_info}/METADATA",
                f"Metadata-Version: 2.4\nName: {distribution}\nVersion: {version}\n",
            )
            archive.writestr(
                f"{dist_info}/WHEEL",
                "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
            )
        return wheel

    def test_offline_wheelhouse_requires_the_dynamic_wheel_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temporary:
            wheelhouse = Path(raw_temporary)
            self.make_build_requirement_wheel(wheelhouse, "setuptools", "68.1.2")
            with self.assertRaisesRegex(SystemExit, "exactly setuptools and wheel"):
                verify_artifact.validate_wheelhouse(wheelhouse)

    def test_offline_wheelhouse_accepts_both_reviewed_build_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temporary:
            wheelhouse = Path(raw_temporary)
            self.make_build_requirement_wheel(wheelhouse, "setuptools", "68.1.2")
            self.make_build_requirement_wheel(wheelhouse, "wheel", "0.41.2")
            inputs = verify_artifact.validate_wheelhouse(wheelhouse)
            self.assertEqual({"setuptools", "wheel"}, set(inputs))

    def test_offline_wheelhouse_rejects_old_setuptools(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temporary:
            wheelhouse = Path(raw_temporary)
            self.make_build_requirement_wheel(wheelhouse, "setuptools", "67.8.0")
            self.make_build_requirement_wheel(wheelhouse, "wheel", "0.41.2")
            with self.assertRaisesRegex(SystemExit, "does not satisfy >=68"):
                verify_artifact.validate_wheelhouse(wheelhouse)

    def test_offline_wheelhouse_rejects_a_prerelease_shortcut(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temporary:
            wheelhouse = Path(raw_temporary)
            self.make_build_requirement_wheel(wheelhouse, "setuptools", "68.0rc1")
            self.make_build_requirement_wheel(wheelhouse, "wheel", "0.41.2")
            with self.assertRaisesRegex(SystemExit, "final numeric release"):
                verify_artifact.validate_wheelhouse(wheelhouse)

    def test_environment_discards_user_pip_and_python_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temporary, mock.patch.dict(
            os.environ,
            {
                "PIP_INDEX_URL": "https://user:secret@example.invalid/simple",
                "PIP_TRUSTED_HOST": "example.invalid",
                "PYTHONPATH": "/untrusted",
                "NETRC": "/secret/netrc",
            },
        ):
            clean = verify_artifact.environment(Path(raw_temporary) / "home")
        self.assertEqual("https://pypi.org/simple", clean["PIP_INDEX_URL"])
        self.assertEqual(os.devnull, clean["PIP_CONFIG_FILE"])
        self.assertEqual(os.devnull, clean["NETRC"])
        self.assertNotIn("PIP_TRUSTED_HOST", clean)
        self.assertNotIn("PYTHONPATH", clean)
        self.assertNotIn("secret", " ".join(clean.values()))
        self.assertEqual(clean["TMPDIR"], clean["TEMP"])
        self.assertEqual(clean["TMPDIR"], clean["TMP"])

    def test_command_display_redacts_temporary_paths(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temporary:
            temporary = Path(raw_temporary)
            display = io.StringIO()
            with contextlib.redirect_stdout(display):
                output = verify_artifact.run(
                    [sys.executable, "-B", "-c", f"print({str(temporary)!r})"],
                    cwd=temporary,
                    env=os.environ.copy(),
                    redactions={temporary: "<temporary>"},
                )
            self.assertIn(str(temporary), output)
            self.assertNotIn(str(temporary), display.getvalue())
            self.assertIn("<temporary>", display.getvalue())

    def test_command_output_limit_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temporary, mock.patch.object(
            verify_artifact, "MAX_OUTPUT_BYTES", 1024
        ), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "exceeded 1024 output bytes"):
                verify_artifact.run(
                    [sys.executable, "-B", "-c", "print('x' * 4096)"],
                    cwd=Path(raw_temporary),
                    env=os.environ.copy(),
                )

    @unittest.skipUnless(os.name == "posix" and Path("/proc").is_dir(), "Linux process probe")
    def test_successful_parent_cannot_leave_a_descendant(self) -> None:
        command = (
            "import subprocess, sys; "
            "child = subprocess.Popen([sys.executable, '-B', '-c', "
            "'import time; time.sleep(60)']); "
            "print(child.pid, flush=True)"
        )
        with tempfile.TemporaryDirectory() as raw_temporary, contextlib.redirect_stdout(
            io.StringIO()
        ):
            output = verify_artifact.run(
                [sys.executable, "-B", "-c", command],
                cwd=Path(raw_temporary),
                env=os.environ.copy(),
            )
        child_pid = int(output.strip())
        deadline = time.monotonic() + 2
        while Path(f"/proc/{child_pid}").exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertFalse(Path(f"/proc/{child_pid}").exists())

    @unittest.skipUnless(os.name == "posix" and Path("/proc").is_dir(), "Linux process probe")
    def test_timeout_kills_a_descendant_that_ignores_sigterm(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temporary:
            temporary = Path(raw_temporary)
            pid_file = temporary / "child.pid"
            child_command = (
                "import signal, time; "
                "signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)"
            )
            parent_command = (
                "import pathlib, subprocess, sys, time; "
                f"child = subprocess.Popen([sys.executable, '-B', '-c', {child_command!r}]); "
                f"pathlib.Path({str(pid_file)!r}).write_text(str(child.pid)); "
                "time.sleep(60)"
            )
            with mock.patch.object(
                verify_artifact, "COMMAND_TIMEOUT_SECONDS", 0.15
            ), mock.patch.object(
                verify_artifact, "TERMINATION_GRACE_SECONDS", 0.1
            ), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, "exceeded 0.15 seconds"):
                    verify_artifact.run(
                        [sys.executable, "-B", "-c", parent_command],
                        cwd=temporary,
                        env=os.environ.copy(),
                    )
            child_pid = int(pid_file.read_text())
            deadline = time.monotonic() + 2
            while Path(f"/proc/{child_pid}").exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertFalse(Path(f"/proc/{child_pid}").exists())

    def test_source_guard_detects_mutation_even_during_failure(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temporary:
            project = Path(raw_temporary)
            source = project / "source.py"
            source.write_text("before\n")
            with mock.patch.object(verify_artifact, "PROJECT", project):
                with self.assertRaisesRegex(RuntimeError, "mutated the source tree"):
                    with verify_artifact.unchanged_source_guard():
                        source.write_text("after\n")
                        raise ValueError("original failure")


if __name__ == "__main__":
    unittest.main()
