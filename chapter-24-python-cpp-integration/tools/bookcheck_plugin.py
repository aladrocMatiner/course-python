#!/usr/bin/env python3
"""Chapter-specific C++ checks for the versioned root book-quality registry."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PLUGIN_ID = "cpp"
API_VERSION = 1
CHAPTER = Path("chapter-24-python-cpp-integration")


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
        CHAPTER / "examples/faststats-cpp/CMakeLists.txt": [
            "CMAKE_CXX_STANDARD 17",
            "FASTSTATS_BUILD_TEST_EXTENSION",
            "FASTSTATS_ENABLE_SANITIZERS",
            "install(TARGETS _native",
            "faststats-sanitizer-status.txt",
        ],
        CHAPTER / "examples/faststats-cpp/cpp/include/faststats_cpp/core.hpp": [
            "max_samples = 1'000'000",
            "max_magnitude = 1e150",
            "class OnlineStats",
        ],
        CHAPTER / "examples/faststats-cpp/cpp/src/core.cpp": [
            "mean += (value - mean) / count",
            "close_to_threshold",
            "normalize_in_place",
        ],
        CHAPTER / "examples/faststats-cpp/cpp/src/bindings.cpp": [
            "PyLong_CheckExact",
            "PyFloat_CheckExact",
            "py::gil_scoped_release",
            "py::smart_holder",
            "py::return_value_policy::reference_internal",
            "py::keep_alive<1, 2>()",
        ],
        CHAPTER / "examples/faststats-cpp/constraints-build.txt": [
            "pybind11==3.0.4",
            "scikit-build-core==1.0.3",
        ],
        CHAPTER / "examples/faststats-cpp/python/faststats_cpp/_native.pyi": [
            "from typing import Never",
            "_native_only: Never",
        ],
        CHAPTER / "examples/faststats-cpp/tools/verify_artifacts.py": [
            "typing_rejections.py",
            '"not found"',
        ],
        CHAPTER / "examples/faststats-cpp/tools/verify_native.py": [
            'sanitizer_status.startswith("enabled:")',
            'sanitizer_status.startswith("unsupported:")',
        ],
    }
    findings: list[dict[str, str]] = []
    for relative, tokens in expected.items():
        absolute = root / relative
        if not absolute.is_file():
            findings.append(
                diagnostic(relative, "missing-source", "required C++ companion source is missing", "restore the tested source")
            )
            continue
        text = absolute.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                findings.append(
                    diagnostic(
                        relative,
                        "contract-token",
                        f"required tested contract token is absent: {token}",
                        "restore the numeric/ownership/GIL contract and rerun verify_all.py",
                    )
                )
    return findings


def check_boundaries(context: dict[str, Any]) -> list[dict[str, str]]:
    root = Path(context["root"])
    findings: list[dict[str, str]] = []
    core_paths = [
        CHAPTER / "examples/faststats-cpp/cpp/include/faststats_cpp/core.hpp",
        CHAPTER / "examples/faststats-cpp/cpp/src/core.cpp",
    ]
    for relative in core_paths:
        path = root / relative
        if path.is_file() and re.search(r"Python\.h|pybind11", path.read_text(encoding="utf-8")):
            findings.append(
                diagnostic(relative, "core-python-boundary", "Python dependency leaked into the autonomous core", "move Python conversion into bindings.cpp")
            )

    cmake_relative = CHAPTER / "examples/faststats-cpp/CMakeLists.txt"
    cmake = root / cmake_relative
    if cmake.is_file():
        text = cmake.read_text(encoding="utf-8")
        if re.search(r"install\s*\([^)]*_faststats_test", text, re.S):
            findings.append(
                diagnostic(cmake_relative, "hook-distribution", "test rendezvous is installed", "install only _native and keep _faststats_test build-local")
            )

    binding_relative = CHAPTER / "examples/faststats-cpp/cpp/src/bindings.cpp"
    binding = root / binding_relative
    if binding.is_file():
        text = binding.read_text(encoding="utf-8")
        release_regions = re.findall(r"py::gil_scoped_release[^;]*;(.{0,350})", text, re.S)
        if any("checked.values" in region or "callback(" in region for region in release_regions):
            findings.append(
                diagnostic(binding_relative, "gil-borrow-boundary", "borrowed buffer or callback appears near a released-GIL region", "release only around core work on copied C++ storage")
            )
    return findings


def register(registry: Any) -> None:
    registry.add(
        plugin_id=PLUGIN_ID,
        api_version=API_VERSION,
        checks={"contract": check_contract, "boundaries": check_boundaries},
        prerequisites=(),
        timeout=30,
    )


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    context = {"root": str(root), "plugin": str(Path(__file__).relative_to(root))}
    findings = check_contract(context) + check_boundaries(context)
    print(json.dumps(findings, indent=2, sort_keys=True))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
