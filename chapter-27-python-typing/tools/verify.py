#!/usr/bin/env python3
"""Bounded, non-installing verifier for the Chapter 27 companion."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final


CHAPTER: Final = Path(__file__).resolve().parents[1]
EXAMPLES: Final = CHAPTER / "examples"
TESTS: Final = CHAPTER / "tests"
LOCK: Final = CHAPTER / "requirements-dev.lock"
TIMEOUT_SECONDS: Final = 20.0
OUTPUT_LIMIT_BYTES: Final = 64 * 1024
EXPECTED_CHECKER_CODES: Final = ("[arg-type]", "[typeddict-item]", "[assignment]")
COPY_FILES: Final = (
    EXAMPLES / "typed_inventory.py",
    EXAMPLES / "checker_positive.py",
    EXAMPLES / "checker_negative.py",
    EXAMPLES / "checker_corrected.py",
    TESTS / "test_typed_inventory.py",
)
FORBIDDEN_DIRS: Final = {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
}
FORBIDDEN_SUFFIXES: Final = {".pyc", ".pyo"}


@dataclass(frozen=True)
class RunResult:
    returncode: int
    output: str
    timed_out: bool = False
    output_limited: bool = False
    surviving_output_holder: bool = False


def _source_snapshot() -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(CHAPTER.rglob("*")):
        if path.is_file():
            relative = path.relative_to(CHAPTER).as_posix()
            snapshot[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def _residue() -> list[str]:
    findings: list[str] = []
    for path in CHAPTER.rglob("*"):
        relative = path.relative_to(CHAPTER).as_posix()
        if path.is_dir() and path.name in FORBIDDEN_DIRS:
            findings.append(relative)
        elif path.is_file() and path.suffix in FORBIDDEN_SUFFIXES:
            findings.append(relative)
    return sorted(findings)


def _terminate_group(process: subprocess.Popen[bytes], *, force: bool) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL if force else signal.SIGTERM)
        elif force:
            process.kill()
        else:
            process.terminate()
    except (ProcessLookupError, PermissionError):
        pass


def _bounded_run(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout: float = TIMEOUT_SECONDS,
) -> RunResult:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=(os.name == "posix"),
    )
    assert process.stdout is not None

    captured = bytearray()
    output_limited = threading.Event()

    def drain() -> None:
        while True:
            chunk = process.stdout.read(4096)
            if not chunk:
                return
            remaining = OUTPUT_LIMIT_BYTES - len(captured)
            if remaining > 0:
                captured.extend(chunk[:remaining])
            if len(chunk) > remaining:
                output_limited.set()

    reader = threading.Thread(target=drain, name="chapter27-output", daemon=True)
    reader.start()
    deadline = time.monotonic() + timeout
    timed_out = False

    while process.poll() is None:
        if output_limited.is_set():
            _terminate_group(process, force=False)
            break
        if time.monotonic() >= deadline:
            timed_out = True
            _terminate_group(process, force=False)
            break
        time.sleep(0.02)

    try:
        process.wait(timeout=0.5)
    except subprocess.TimeoutExpired:
        _terminate_group(process, force=True)
        process.wait(timeout=1.0)

    reader.join(timeout=0.5)
    surviving_output_holder = reader.is_alive()
    if surviving_output_holder:
        _terminate_group(process, force=True)
        reader.join(timeout=0.5)

    text = bytes(captured).decode("utf-8", errors="replace")
    return RunResult(
        returncode=process.returncode,
        output=text,
        timed_out=timed_out,
        output_limited=output_limited.is_set(),
        surviving_output_holder=surviving_output_holder,
    )


def _safe_environment(temp: Path) -> dict[str, str]:
    environment: dict[str, str] = {
        "HOME": str(temp / "home"),
        "MYPY_FORCE_COLOR": "0",
        "NO_COLOR": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TMP": str(temp / "tmp"),
        "TEMP": str(temp / "tmp"),
        "TMPDIR": str(temp / "tmp"),
        "XDG_CACHE_HOME": str(temp / "cache"),
    }
    for name in ("PATH", "SYSTEMROOT", "WINDIR"):
        if name in os.environ:
            environment[name] = os.environ[name]
    for path in (temp / "home", temp / "tmp", temp / "cache"):
        path.mkdir(parents=True, exist_ok=True)
    return environment


def _copy_declared_inputs(temp: Path) -> None:
    for source in COPY_FILES:
        relative = source.relative_to(CHAPTER)
        destination = temp / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def _redact(output: str, temp: Path) -> str:
    redacted = output.replace(str(CHAPTER.parent), "<repo>")
    redacted = redacted.replace(str(temp), "<temp>")
    return redacted[-OUTPUT_LIMIT_BYTES:]


def _require_clean_result(result: RunResult, phase: str, temp: Path) -> bool:
    if result.timed_out:
        print(f"{phase}: failed (timeout after {TIMEOUT_SECONDS:g}s)", file=sys.stderr)
        return False
    if result.output_limited:
        print(f"{phase}: failed (output exceeded {OUTPUT_LIMIT_BYTES} bytes)", file=sys.stderr)
        return False
    if result.surviving_output_holder:
        print(f"{phase}: failed (a descendant retained the output pipe)", file=sys.stderr)
        return False
    if result.returncode != 0:
        print(f"{phase}: failed (exit {result.returncode})", file=sys.stderr)
        output = _redact(result.output, temp).strip()
        if output:
            print(output, file=sys.stderr)
        return False
    return True


def _parse_mypy_pin() -> str:
    pins = [
        line.strip()
        for line in LOCK.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(pins) != 1 or not pins[0].startswith("mypy=="):
        raise ValueError("requirements-dev.lock must contain one exact mypy pin")
    version = pins[0].partition("==")[2]
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)+", version):
        raise ValueError("the mypy pin must be an exact numeric version")
    return version


def _mypy_command(temp: Path, *filenames: str) -> list[str]:
    return [
        sys.executable,
        "-I",
        "-B",
        "-m",
        "mypy",
        "--strict",
        "--python-version=3.11",
        "--show-error-codes",
        "--no-error-summary",
        "--no-pretty",
        "--no-color-output",
        "--no-incremental",
        f"--cache-dir={temp / 'mypy-cache'}",
        "typed_inventory.py",
        *filenames,
    ]


def _run_runtime(temp: Path, environment: dict[str, str]) -> bool:
    result = _bounded_run(
        [
            sys.executable,
            "-I",
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_*.py",
        ],
        cwd=temp,
        environment=environment,
    )
    if not _require_clean_result(result, "runtime", temp):
        return False

    match = re.search(r"Ran ([0-9]+) tests?", result.output)
    count = match.group(1) if match else "unknown"
    print("runtime: passed")
    print(f"interpreter: {sys.implementation.name} {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"tests: {count}")
    print(f"timeout-seconds: {TIMEOUT_SECONDS:g}")
    return True


def _run_checker(temp: Path, environment: dict[str, str]) -> tuple[bool, bool]:
    try:
        pin = _parse_mypy_pin()
    except (OSError, ValueError) as error:
        print(f"checker: failed ({error})", file=sys.stderr)
        return False, False

    version_result = _bounded_run(
        [sys.executable, "-I", "-B", "-m", "mypy", "--version"],
        cwd=temp,
        environment=environment,
        timeout=5.0,
    )
    version_match = re.search(r"\bmypy ([0-9]+(?:\.[0-9]+)+)", version_result.output)
    if version_result.returncode != 0 or version_match is None:
        print(
            f"checker: prerequisite missing (requires mypy=={pin} in the current interpreter)",
            file=sys.stderr,
        )
        return False, True
    observed = version_match.group(1)
    if observed != pin:
        print(
            f"checker: prerequisite missing (requires mypy=={pin}; observed {observed})",
            file=sys.stderr,
        )
        return False, True

    examples = temp / "examples"
    positive = _bounded_run(
        _mypy_command(temp, "checker_positive.py"),
        cwd=examples,
        environment=environment,
    )
    if not _require_clean_result(positive, "checker-positive", temp):
        return False, False

    negative = _bounded_run(
        _mypy_command(temp, "checker_negative.py"),
        cwd=examples,
        environment=environment,
    )
    if negative.timed_out or negative.output_limited or negative.surviving_output_holder:
        _require_clean_result(negative, "checker-negative", temp)
        return False, False
    if negative.returncode == 0:
        print("checker-negative: failed (expected non-zero exit)", file=sys.stderr)
        return False, False
    missing_codes = [code for code in EXPECTED_CHECKER_CODES if code not in negative.output]
    if missing_codes:
        print(
            "checker-negative: failed (missing categories: " + ", ".join(missing_codes) + ")",
            file=sys.stderr,
        )
        print(_redact(negative.output, temp).strip(), file=sys.stderr)
        return False, False

    corrected = _bounded_run(
        _mypy_command(temp, "checker_corrected.py"),
        cwd=examples,
        environment=environment,
    )
    if not _require_clean_result(corrected, "checker-corrected", temp):
        return False, False

    print("checker: passed")
    print(f"mypy: {observed}")
    print("positive: passed")
    print("negative: expected failure (arg-type, typeddict-item, assignment)")
    print("corrected: passed")
    print(f"timeout-seconds: {TIMEOUT_SECONDS:g}")
    return True, False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--runtime", action="store_true", help="run standard-library runtime tests")
    mode.add_argument("--checker", action="store_true", help="run the provisioned pinned checker contract")
    arguments = parser.parse_args(argv)

    before = _source_snapshot()
    initial_residue = _residue()
    if initial_residue:
        print("cleanup: failed (pre-existing residue: " + ", ".join(initial_residue) + ")", file=sys.stderr)
        return 1

    prerequisite_missing = False
    with tempfile.TemporaryDirectory(prefix="chapter27-typing-") as raw_temp:
        temp = Path(raw_temp)
        _copy_declared_inputs(temp)
        environment = _safe_environment(temp)
        if arguments.runtime:
            passed = _run_runtime(temp, environment)
        else:
            passed, prerequisite_missing = _run_checker(temp, environment)

    after = _source_snapshot()
    residue = _residue()
    if before != after:
        print("cleanup: failed (chapter source changed during verification)", file=sys.stderr)
        return 1
    if residue:
        print("cleanup: failed (residue: " + ", ".join(residue) + ")", file=sys.stderr)
        return 1
    if not passed:
        return 2 if prerequisite_missing else 1
    print("cleanup: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

