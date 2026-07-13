#!/usr/bin/env python3
"""Read-only chapter 25 toolchain preflight."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PINNED_RUST = "1.97.0"
PINNED_MATURIN = "1.14.1"


def capture(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=20,
    )
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-venv", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    if sys.version_info < (3, 11):
        errors.append("CPython 3.11 or later is required")
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if args.require_venv and not in_venv:
        errors.append("activate a Python virtual environment before building")
    for tool in ("rustup", "cc"):
        if shutil.which(tool) is None:
            errors.append(f"required tool is missing from PATH: {tool}")
    report: dict[str, object] = {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "architecture": platform.machine(),
        "platform": platform.system(),
        "venv_active": in_venv,
        "rust_toolchain": PINNED_RUST,
    }
    if shutil.which("rustup"):
        try:
            rustc = capture(["rustup", "run", PINNED_RUST, "rustc", "--version"])
            cargo = capture(["rustup", "run", PINNED_RUST, "cargo", "--version"])
            host = capture(["rustup", "run", PINNED_RUST, "rustc", "-vV"])
            report.update(rustc=rustc, cargo=cargo, host=host)
            if f"rustc {PINNED_RUST}" not in rustc:
                errors.append(f"rustup did not activate pinned Rust {PINNED_RUST}")
        except (subprocess.SubprocessError, OSError) as error:
            errors.append(
                f"cannot activate Rust {PINNED_RUST}; run "
                f"`rustup toolchain install {PINNED_RUST} --component rustfmt --component clippy`: {error}"
            )
    try:
        maturin = capture([sys.executable, "-m", "maturin", "--version"])
        report["maturin"] = maturin
        if PINNED_MATURIN not in maturin:
            errors.append(f"maturin {PINNED_MATURIN} is required, found: {maturin}")
    except (subprocess.SubprocessError, OSError):
        errors.append(
            f"maturin is missing; install exact development tools from "
            f"{Path('examples/faststats-rs/requirements-dev.lock')}"
        )
    report["errors"] = errors
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for key, value in report.items():
            if key != "errors":
                print(f"{key}: {value}")
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
