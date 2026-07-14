#!/usr/bin/env python3
"""Build and verify the Chapter 15 wheel without mutating the checkout."""

from __future__ import annotations

import argparse
import base64
import binascii
import configparser
import csv
import hashlib
import io
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import venv
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from email import policy
from email.message import Message
from email.parser import BytesParser
from pathlib import Path
from pathlib import PurePosixPath


PROJECT = Path(__file__).resolve().parents[1]
EXPECTED_WHEEL_NAME = "course_mi_app-0.1.0-py3-none-any.whl"
DIST_INFO = "course_mi_app-0.1.0.dist-info"
EXPECTED_PACKAGE_FILES = {
    "mi_app/__init__.py",
    "mi_app/cli.py",
    "mi_app/domain.py",
}
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
COMMAND_TIMEOUT_SECONDS = 300
TERMINATION_GRACE_SECONDS = 2.0


def create_windows_job(process: subprocess.Popen[bytes]) -> object | None:
    if os.name != "nt":
        return None
    import ctypes
    from ctypes import wintypes

    class IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class BasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class ExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimitInformation),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        raise OSError(ctypes.get_last_error(), "CreateJobObjectW failed")
    information = ExtendedLimitInformation()
    information.BasicLimitInformation.LimitFlags = 0x00002000
    if not kernel32.SetInformationJobObject(
        job, 9, ctypes.byref(information), ctypes.sizeof(information)
    ):
        error = ctypes.get_last_error()
        kernel32.CloseHandle(job)
        raise OSError(error, "SetInformationJobObject failed")
    process_handle = wintypes.HANDLE(int(process._handle))  # type: ignore[attr-defined]
    if not kernel32.AssignProcessToJobObject(job, process_handle):
        error = ctypes.get_last_error()
        kernel32.CloseHandle(job)
        raise OSError(error, "AssignProcessToJobObject failed")
    return job


def close_windows_job(job: object | None) -> None:
    if job is None:
        return
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    if not kernel32.CloseHandle(job):
        raise OSError(ctypes.get_last_error(), "CloseHandle(job) failed")


def posix_group_exists(process_group: int) -> bool:
    try:
        os.killpg(process_group, 0)
    except ProcessLookupError:
        return False
    return True


def terminate_process_tree(process: subprocess.Popen[bytes]) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        )
        if process.poll() is None:
            process.kill()
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + TERMINATION_GRACE_SECONDS
    while posix_group_exists(process.pid) and time.monotonic() < deadline:
        time.sleep(0.02)
    if posix_group_exists(process.pid):
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def redact(text: str, redactions: dict[Path, str]) -> str:
    for path, replacement in sorted(
        redactions.items(), key=lambda item: len(str(item[0])), reverse=True
    ):
        text = text.replace(str(path), replacement)
    return text


def run(
    command: list[os.PathLike[str] | str],
    *,
    cwd: Path,
    env: dict[str, str],
    redactions: dict[Path, str] | None = None,
) -> str:
    rendered = [str(part) for part in command]
    redactions = redactions or {}
    display_command = redact(" ".join(rendered), redactions)
    display_cwd = redact(str(cwd), redactions)
    print(f"+ ({display_cwd}) {display_command}", flush=True)
    popen_options: dict[str, object] = {}
    popen_command = rendered
    if os.name == "nt":
        popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        launcher = (
            "import subprocess, sys; "
            "sys.stdin.buffer.read(1); "
            "raise SystemExit(subprocess.run(sys.argv[1:]).returncode)"
        )
        popen_command = [sys.executable, "-B", "-c", launcher, *rendered]
        popen_options["stdin"] = subprocess.PIPE
    else:
        popen_options["start_new_session"] = True
    process = subprocess.Popen(
        popen_command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **popen_options,
    )
    try:
        windows_job = create_windows_job(process)
    except OSError as error:
        terminate_process_tree(process)
        process.wait(timeout=10)
        if process.stdout is not None:
            process.stdout.close()
        raise RuntimeError(f"could not establish bounded process cleanup: {error}") from error
    if os.name == "nt":
        assert process.stdin is not None
        process.stdin.write(b"1")
        process.stdin.close()
    assert process.stdout is not None
    captured = bytearray()
    output_limit_hit = threading.Event()

    def drain_output() -> None:
        while chunk := process.stdout.read(64 * 1024):
            remaining = MAX_OUTPUT_BYTES - len(captured)
            if remaining > 0:
                captured.extend(chunk[:remaining])
            if len(chunk) > remaining:
                output_limit_hit.set()

    reader = threading.Thread(target=drain_output, daemon=True)
    reader.start()
    deadline = time.monotonic() + COMMAND_TIMEOUT_SECONDS
    failure_reason = ""
    while process.poll() is None:
        if output_limit_hit.wait(timeout=0.05):
            failure_reason = f"command exceeded {MAX_OUTPUT_BYTES} output bytes"
            break
        if time.monotonic() >= deadline:
            failure_reason = f"command exceeded {COMMAND_TIMEOUT_SECONDS} seconds"
            break
    cleanup_errors: list[str] = []
    try:
        terminate_process_tree(process)
    except (OSError, subprocess.SubprocessError) as error:
        cleanup_errors.append(f"process-tree cleanup failed: {error}")
    try:
        close_windows_job(windows_job)
    except OSError as error:
        cleanup_errors.append(f"Windows job cleanup failed: {error}")
    if process.poll() is None:
        process.kill()
        process.wait(timeout=10)
    return_code = process.wait()
    reader.join(timeout=5)
    process.stdout.close()
    output = captured.decode("utf-8", errors="replace")
    display_output = redact(output, redactions)
    if output_limit_hit.is_set() and not failure_reason:
        failure_reason = f"command exceeded {MAX_OUTPUT_BYTES} output bytes"
    if cleanup_errors and not failure_reason:
        failure_reason = "; ".join(cleanup_errors)
    if display_output:
        print(
            display_output,
            end="" if display_output.endswith("\n") else "\n",
        )
    if failure_reason:
        raise RuntimeError(f"{failure_reason}: {display_command}\n{display_output}")
    if return_code != 0:
        raise RuntimeError(
            f"command failed with exit {return_code}: {display_command}\n{display_output}"
        )
    return output


def environment(temporary_home: Path) -> dict[str, str]:
    temporary_home.mkdir()
    process_temporary = temporary_home.parent / "process-temp"
    process_temporary.mkdir()
    clean = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("PIP_", "PYTHON"))
        and key not in {"NETRC", "VIRTUAL_ENV"}
    }
    clean.update(
        {
            "HOME": str(temporary_home),
            "USERPROFILE": str(temporary_home),
            "XDG_CACHE_HOME": str(temporary_home / "cache"),
            "XDG_CONFIG_HOME": str(temporary_home / "config"),
            "NETRC": os.devnull,
            "PIP_CONFIG_FILE": os.devnull,
            "PIP_INDEX_URL": "https://pypi.org/simple",
            "PIP_CACHE_DIR": str(temporary_home / "pip-cache"),
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_INPUT": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "TMPDIR": str(process_temporary),
            "TEMP": str(process_temporary),
            "TMP": str(process_temporary),
        }
    )
    return clean


def venv_python(directory: Path) -> Path:
    relative = Path("Scripts/python.exe") if os.name == "nt" else Path("bin/python")
    return directory / relative


def console_entry_point(directory: Path) -> Path:
    relative = Path("Scripts/mi-app.exe") if os.name == "nt" else Path("bin/mi-app")
    return directory / relative


def normalized_distribution(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def validate_wheelhouse(directory: Path) -> dict[str, tuple[str, Path]]:
    wheel_paths = sorted(directory.glob("*.whl"))
    if len(wheel_paths) != 2:
        raise SystemExit("wheelhouse must contain exactly setuptools and wheel artifacts")
    inputs: dict[str, tuple[str, Path]] = {}
    for path in wheel_paths:
        try:
            with zipfile.ZipFile(path) as archive:
                if archive.testzip() is not None:
                    raise RuntimeError("a member failed its CRC check")
                names = set(archive.namelist())
                metadata_files = sorted(
                    name
                    for name in names
                    if name.count("/") == 1 and name.endswith(".dist-info/METADATA")
                )
                wheel_files = sorted(
                    name
                    for name in names
                    if name.count("/") == 1 and name.endswith(".dist-info/WHEEL")
                )
                if len(metadata_files) != 1 or len(wheel_files) != 1:
                    raise RuntimeError("expected one METADATA and one WHEEL file")
                if metadata_files[0].split("/", 1)[0] != wheel_files[0].split("/", 1)[0]:
                    raise RuntimeError("METADATA and WHEEL use different dist-info roots")
                metadata = parse_message(archive.read(metadata_files[0]), "build METADATA")
                wheel_metadata = parse_message(
                    archive.read(wheel_files[0]), "build WHEEL"
                )
        except (OSError, RuntimeError, zipfile.BadZipFile) as error:
            raise SystemExit(f"invalid wheelhouse artifact {path.name}: {error}") from error
        names = metadata.get_all("Name")
        versions = metadata.get_all("Version")
        if len(names or []) != 1 or len(versions or []) != 1:
            raise SystemExit(f"invalid name/version metadata in {path.name}")
        distribution = normalized_distribution(names[0])
        version = versions[0]
        if distribution not in {"setuptools", "wheel"}:
            raise SystemExit(f"unexpected wheelhouse distribution: {distribution}")
        if distribution in inputs:
            raise SystemExit(f"duplicate wheelhouse distribution: {distribution}")
        if "py3-none-any" not in (wheel_metadata.get_all("Tag") or []):
            raise SystemExit(f"incompatible build wheel tag for {distribution}: {path.name}")
        inputs[distribution] = (version, path)

    missing = {"setuptools", "wheel"} - set(inputs)
    if missing:
        raise SystemExit(f"wheelhouse is missing build wheels: {sorted(missing)}")
    setuptools_version = inputs["setuptools"][0]
    if re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", setuptools_version) is None:
        raise SystemExit(
            "wheelhouse setuptools must use a final numeric release for this lesson: "
            f"{setuptools_version}"
        )
    release = tuple(int(part) for part in setuptools_version.split("."))
    if release < (68,):
        raise SystemExit(
            f"wheelhouse setuptools version does not satisfy >=68: {setuptools_version}"
        )
    return inputs


def assert_source_hygiene() -> None:
    forbidden: list[Path] = []
    for path in PROJECT.rglob("*"):
        if path.is_dir() and (
            path.name
            in {"__pycache__", ".pytest_cache", "build", "dist", ".venv", "venv"}
            or path.name.endswith(".egg-info")
        ):
            forbidden.append(path)
        elif path.is_file() and (
            path.suffix in {".pyc", ".pyo", ".whl", ".so", ".pyd"}
            or path.name.endswith(".tar.gz")
            or path.name == ".coverage"
        ):
            forbidden.append(path)
    if forbidden:
        rendered = [path.relative_to(PROJECT).as_posix() for path in forbidden]
        raise RuntimeError(f"source tree contains generated artifacts: {rendered}")


def source_snapshot() -> dict[str, str]:
    return {
        path.relative_to(PROJECT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in PROJECT.rglob("*")
        if path.is_file()
    }


def assert_source_unchanged(before: dict[str, str]) -> None:
    after = source_snapshot()
    if before == after:
        return
    before_paths = set(before)
    after_paths = set(after)
    added = sorted(after_paths - before_paths)
    removed = sorted(before_paths - after_paths)
    changed = sorted(
        path for path in before_paths & after_paths if before[path] != after[path]
    )
    raise RuntimeError(
        "artifact verification mutated the source tree: "
        f"added={added}, removed={removed}, changed={changed}"
    )


@contextmanager
def unchanged_source_guard() -> Iterator[None]:
    assert_source_hygiene()
    before = source_snapshot()
    try:
        yield
    finally:
        assert_source_hygiene()
        assert_source_unchanged(before)


def parse_message(raw: bytes, description: str) -> Message:
    message = BytesParser(policy=policy.default).parsebytes(raw)
    if message.defects:
        raise RuntimeError(f"wheel {description} is malformed: {message.defects}")
    return message


def inspect_wheel(wheel: Path, source_root: Path = PROJECT / "src") -> None:
    if wheel.name != EXPECTED_WHEEL_NAME:
        raise RuntimeError(f"unexpected wheel filename/tag: {wheel.name}")
    with zipfile.ZipFile(wheel) as archive:
        members = archive.infolist()
        if len(members) > 64 or sum(member.file_size for member in members) > 1_000_000:
            raise RuntimeError("wheel exceeds the lesson's file-count or size boundary")
        raw_names = [member.filename for member in members if not member.is_dir()]
        names = set(raw_names)
        if len(raw_names) != len(names):
            raise RuntimeError("wheel contains duplicate member names")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                raise RuntimeError(f"wheel contains an unsafe member path: {name}")
        corrupt = archive.testzip()
        if corrupt is not None:
            raise RuntimeError(f"wheel member failed its CRC check: {corrupt}")

        missing = EXPECTED_PACKAGE_FILES - names
        if missing:
            raise RuntimeError(f"wheel is missing package files: {sorted(missing)}")
        if any(name.startswith("src/") for name in names):
            raise RuntimeError("wheel leaked the source-layout container directory")
        unexpected_top_level = sorted(
            name
            for name in names
            if name not in EXPECTED_PACKAGE_FILES
            and not name.startswith(f"{DIST_INFO}/")
        )
        if unexpected_top_level:
            raise RuntimeError(
                f"wheel contains unexpected top-level files: {unexpected_top_level}"
            )
        for name in EXPECTED_PACKAGE_FILES:
            if archive.read(name) != (source_root / name).read_bytes():
                raise RuntimeError(f"wheel module differs from the reviewed source: {name}")

        dist_info_roots = {
            name.split("/", 1)[0] for name in names if ".dist-info/" in name
        }
        if dist_info_roots != {DIST_INFO}:
            raise RuntimeError(f"wheel has unexpected dist-info roots: {dist_info_roots}")
        required_metadata = {
            f"{DIST_INFO}/METADATA",
            f"{DIST_INFO}/WHEEL",
            f"{DIST_INFO}/entry_points.txt",
            f"{DIST_INFO}/top_level.txt",
            f"{DIST_INFO}/RECORD",
        }
        missing_metadata = required_metadata - names
        if missing_metadata:
            raise RuntimeError(f"wheel is missing metadata files: {sorted(missing_metadata)}")
        unexpected_metadata = sorted(
            name
            for name in names
            if name.startswith(f"{DIST_INFO}/") and name not in required_metadata
        )
        if unexpected_metadata:
            raise RuntimeError(
                f"wheel contains unexpected dist-info files: {unexpected_metadata}"
            )

        metadata = parse_message(archive.read(f"{DIST_INFO}/METADATA"), "METADATA")
        if metadata.get_all("Name") != ["course-mi-app"] or metadata.get_all(
            "Version"
        ) != ["0.1.0"]:
            raise RuntimeError("wheel metadata name/version does not match pyproject.toml")
        if metadata.get_all("Requires-Python") != [">=3.11"]:
            raise RuntimeError("wheel Requires-Python does not match pyproject.toml")

        wheel_metadata = parse_message(archive.read(f"{DIST_INFO}/WHEEL"), "WHEEL")
        if (
            wheel_metadata.get("Root-Is-Purelib", "").lower() != "true"
            or wheel_metadata.get_all("Tag") != ["py3-none-any"]
        ):
            raise RuntimeError("wheel metadata does not prove the expected pure-Python tag")

        entry_points = configparser.ConfigParser(interpolation=None)
        entry_points.optionxform = str
        try:
            entry_points.read_string(
                archive.read(f"{DIST_INFO}/entry_points.txt").decode("utf-8")
            )
        except (UnicodeDecodeError, configparser.Error) as error:
            raise RuntimeError(f"wheel entry_points.txt is malformed: {error}") from error
        if entry_points.sections() != ["console_scripts"] or dict(
            entry_points["console_scripts"]
        ) != {"mi-app": "mi_app.cli:main"}:
            raise RuntimeError("wheel is missing the documented mi-app console entry point")
        if archive.read(f"{DIST_INFO}/top_level.txt") != b"mi_app\n":
            raise RuntimeError("wheel top_level.txt does not name only mi_app")

        try:
            rows = list(
                csv.reader(
                    io.StringIO(archive.read(f"{DIST_INFO}/RECORD").decode("utf-8"))
                )
            )
        except UnicodeDecodeError as error:
            raise RuntimeError("wheel RECORD is not UTF-8") from error
        if any(len(row) != 3 for row in rows):
            raise RuntimeError("wheel RECORD contains a malformed row")
        record_paths = [row[0] for row in rows]
        if len(record_paths) != len(set(record_paths)) or set(record_paths) != names:
            raise RuntimeError("wheel RECORD does not exactly inventory its members")
        record_path = f"{DIST_INFO}/RECORD"
        for path, digest, size in rows:
            if path == record_path:
                if digest or size:
                    raise RuntimeError("wheel RECORD must not hash itself")
                continue
            if not digest.startswith("sha256=") or not size.isdigit():
                raise RuntimeError(f"wheel RECORD lacks hash/size evidence for {path}")
            content = archive.read(path)
            encoded_digest = digest.removeprefix("sha256=")
            try:
                recorded_digest = base64.b64decode(
                    encoded_digest + "=" * (-len(encoded_digest) % 4),
                    altchars=b"-_",
                    validate=True,
                )
            except (ValueError, binascii.Error) as error:
                raise RuntimeError(f"wheel RECORD digest is malformed for {path}") from error
            if recorded_digest != hashlib.sha256(content).digest():
                raise RuntimeError(f"wheel RECORD digest does not match {path}")
            if int(size) != len(content):
                raise RuntimeError(f"wheel RECORD size does not match {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wheelhouse",
        type=Path,
        help=(
            "reviewed directory containing compatible setuptools>=68 and wheel "
            "distributions; enables a no-index build"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    wheelhouse = args.wheelhouse.resolve() if args.wheelhouse else None
    if wheelhouse is not None and not wheelhouse.is_dir():
        raise SystemExit(f"wheelhouse is not a directory: {wheelhouse}")
    wheelhouse_inputs: dict[str, tuple[str, Path]] = {}
    if wheelhouse is not None:
        wheelhouse_inputs = validate_wheelhouse(wheelhouse)

    print(
        f"host={platform.system()} {platform.machine()}; "
        f"python={platform.python_version()}"
    )
    for distribution, (version, path) in sorted(wheelhouse_inputs.items()):
        print(
            f"wheelhouse-input={distribution}=={version}; "
            f"sha256={hashlib.sha256(path.read_bytes()).hexdigest()}"
        )
    with unchanged_source_guard(), tempfile.TemporaryDirectory(
        prefix="course-mi-app-verify-"
    ) as raw_temporary:
        temporary = Path(raw_temporary)
        clean_env = environment(temporary / "home")
        redactions = {temporary: "<temporary>", PROJECT: "<repo>"}
        if wheelhouse is not None:
            redactions[wheelhouse] = "<wheelhouse>"
        source_copy = temporary / "source"
        shutil.copytree(
            PROJECT,
            source_copy,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "*.pyo", "*.egg-info", "build", "dist"
            ),
        )

        build_environment = temporary / "build-venv"
        venv.EnvBuilder(with_pip=True).create(build_environment)
        build_python = venv_python(build_environment)
        wheels = temporary / "wheels"
        wheels.mkdir()
        build_command: list[os.PathLike[str] | str] = [
            build_python,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--wheel-dir",
            wheels,
        ]
        if wheelhouse is not None:
            build_command.extend(["--no-index", "--find-links", wheelhouse])
        build_command.append(source_copy)
        run(build_command, cwd=temporary, env=clean_env, redactions=redactions)

        built_wheels = sorted(wheels.glob("course_mi_app-0.1.0-*.whl"))
        if len(built_wheels) != 1:
            raise RuntimeError(f"expected exactly one project wheel, found {built_wheels}")
        wheel = built_wheels[0]
        inspect_wheel(wheel)
        digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
        print(f"wheel={wheel.name}; sha256={digest}")

        install_environment = temporary / "install-venv"
        venv.EnvBuilder(with_pip=True).create(install_environment)
        install_python = venv_python(install_environment)
        run(
            [install_python, "-m", "pip", "install", "--no-deps", "--no-index", wheel],
            cwd=temporary,
            env=clean_env,
            redactions=redactions,
        )
        run(
            [install_python, "-m", "pip", "check"],
            cwd=temporary,
            env=clean_env,
            redactions=redactions,
        )

        foreign = temporary / "foreign-working-directory"
        foreign.mkdir()
        import_probe = (
            "from importlib.metadata import version; "
            "import mi_app; "
            "assert version('course-mi-app') == '0.1.0'; "
            "print(mi_app.__name__)"
        )
        imported = run(
            [install_python, "-B", "-c", import_probe],
            cwd=foreign,
            env=clean_env,
            redactions=redactions,
        )
        if imported.strip() != "mi_app":
            raise RuntimeError(f"unexpected foreign-directory import output: {imported!r}")
        cli_output = run(
            [console_entry_point(install_environment)],
            cwd=foreign,
            env=clean_env,
            redactions=redactions,
        )
        if cli_output.strip() != "Order 1: 90.00":
            raise RuntimeError(f"unexpected CLI output: {cli_output!r}")
        run(
            [
                install_python,
                "-B",
                "-m",
                "unittest",
                "discover",
                "-s",
                PROJECT / "tests",
                "-p",
                "test_domain.py",
                "-v",
            ],
            cwd=foreign,
            env=clean_env,
            redactions=redactions,
        )

    print("isolated build -> inspected wheel -> exact install -> foreign-cwd checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
