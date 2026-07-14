#!/usr/bin/env python3
"""Chapter-specific Rust checks for the versioned root book-quality registry."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PLUGIN_ID = "rust"
API_VERSION = 1
CHAPTER = Path("chapter-25-python-rust-integration")


def diagnostic(path: Path, rule: str, message: str, remediation: str) -> dict[str, str]:
    return {
        "rule_id": rule,
        "path": path.as_posix(),
        "message": message,
        "remediation": remediation,
        "construct": f"{rule}:{path.as_posix()}",
    }


def check_contract(context: dict[str, Any]) -> list[dict[str, str]]:
    root = Path(context["root"])
    expected = {
        CHAPTER / "examples/faststats-rs/Cargo.toml": [
            'rust-version = "1.97.0"',
            'pyo3 = "=0.29.0"',
            'abi3-py311 = ["pyo3/abi3-py311"]',
            "test-hooks = []",
        ],
        CHAPTER / "examples/faststats-rs/rust-toolchain.toml": [
            'channel = "1.97.0"',
        ],
        CHAPTER / "examples/faststats-rs/pyproject.toml": [
            'requires = ["maturin==1.14.1"]',
            'module-name = "faststats_rs._native"',
        ],
        CHAPTER / "examples/faststats-rs/src/lib.rs": [
            "#[pymodule(gil_used = true)]",
            "py.detach",
            "mod domain;",
            "PyRuntimeError::new_err",
        ],
        CHAPTER / "examples/faststats-rs/src/domain.rs": [
            "pub const MAX_SAMPLES: usize = 1_000_000;",
            "pub const MAX_ABS_VALUE: f64 = 1.0e150;",
        ],
        CHAPTER / "examples/faststats-rs/benchmarks/benchmark.py": [
            '"anomaly_count", "anomaly_ratio"',
            "math.isclose",
            "assert_error_contract",
            "timed-repetitions=",
        ],
        CHAPTER / "tools/preflight.py": [
            '("cl", "clang-cl")',
        ],
    }
    results: list[dict[str, str]] = []
    for relative, tokens in expected.items():
        absolute = root / relative
        if not absolute.is_file():
            results.append(
                diagnostic(relative, "missing-source", "required Rust source is missing", "restore the tested companion source")
            )
            continue
        text = absolute.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                results.append(
                    diagnostic(
                        relative,
                        "contract-token",
                        f"required tested contract token is absent: {token}",
                        "restore the pinned Rust/PyO3/package contract and rerun verify.py",
                    )
                )
    return results


def check_distribution_boundary(context: dict[str, Any]) -> list[dict[str, str]]:
    root = Path(context["root"])
    relative = CHAPTER / "examples/faststats-rs/Cargo.toml"
    manifest = root / relative
    if not manifest.is_file():
        return [diagnostic(relative, "missing-manifest", "Cargo.toml is missing", "restore the capstone manifest")]
    text = manifest.read_text(encoding="utf-8")
    if '"src/test_hooks.rs"' in text:
        return [
            diagnostic(
                relative,
                "hook-distribution",
                "test-only rendezvous source is included in the Cargo package",
                "keep src/test_hooks.rs outside the manifest include list and inspect the sdist",
            )
        ]
    return []


def register(registry: Any) -> None:
    registry.add(
        plugin_id=PLUGIN_ID,
        api_version=API_VERSION,
        checks={
            "contract": check_contract,
            "distribution-boundary": check_distribution_boundary,
        },
        prerequisites=(),
        timeout=30,
    )


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    context = {"root": str(root), "plugin": str(Path(__file__).relative_to(root))}
    findings = check_contract(context) + check_distribution_boundary(context)
    print(json.dumps(findings, indent=2, sort_keys=True))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
