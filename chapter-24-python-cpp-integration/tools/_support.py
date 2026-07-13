"""Shared bounded subprocess helpers for chapter 24 verification."""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path
from typing import Iterable

CHAPTER = Path(__file__).resolve().parents[1]
LOCK = CHAPTER / "examples" / "faststats-cpp" / "requirements-dev.lock"
CONSTRAINTS = CHAPTER / "examples" / "faststats-cpp" / "constraints-build.txt"


def executable(environment: Path, name: str) -> Path:
    directory = "Scripts" if os.name == "nt" else "bin"
    suffix = ".exe" if os.name == "nt" else ""
    return environment / directory / f"{name}{suffix}"


def environment_with(environment: Path, **extra: str) -> dict[str, str]:
    result = os.environ.copy()
    result["PATH"] = f"{executable(environment, 'python').parent}{os.pathsep}{result.get('PATH', '')}"
    result["PIP_BUILD_CONSTRAINT"] = str(CONSTRAINTS)
    result["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    result["PYTHONDONTWRITEBYTECODE"] = "1"
    result.update(extra)
    return result


def run(
    command: Iterable[os.PathLike[str] | str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = 300,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    rendered = [str(part) for part in command]
    print("+", " ".join(rendered), flush=True)
    return subprocess.run(
        rendered,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        timeout=timeout,
        capture_output=capture,
    )


def create_dev_environment(destination: Path) -> Path:
    venv.EnvBuilder(with_pip=True, clear=True).create(destination)
    python = executable(destination, "python")
    run(
        [python, "-m", "pip", "install", "--requirement", LOCK],
        cwd=destination.parent,
        env=environment_with(destination),
        timeout=600,
    )
    return python


def require_python_311() -> None:
    if sys.version_info < (3, 11):
        raise SystemExit("chapter 24 requires CPython 3.11 or later")
