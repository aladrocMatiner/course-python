"""Minimal domain checks for Appendix C's deterministic companions.

Process containment, aggregate time, output limits, and mutation detection belong
to the repository's generic plugin runner.  This adapter only selects one known
standard-library test module and converts its exit status into one bounded
diagnostic.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Final


PLUGIN_ID: Final = "patterns"
API_VERSION: Final = 1
TEST_DIRECTORY: Final = "appendix-software-design-patterns/examples/tests"


def _diagnostic(
    *, rule_id: str, path: str, message: str, remediation: str, construct: str
) -> dict[str, str]:
    return {
        "rule_id": rule_id,
        "path": path,
        "message": message,
        "remediation": remediation,
        "construct": construct,
    }


def _run_suite(
    context: dict[str, Any], *, filename: str, check_id: str
) -> list[dict[str, str]]:
    relative_test = f"{TEST_DIRECTORY}/{filename}"
    raw_root = Path(context["root"])
    try:
        root = raw_root.resolve(strict=True)
    except OSError:
        return [
            _diagnostic(
                rule_id="invalid-root",
                path=relative_test,
                message="the repository root for the Appendix C check is unavailable",
                remediation="run the check from a readable repository checkout",
                construct=f"invalid-root:{check_id}",
            )
        ]

    test_file = root
    for component in Path(relative_test).parts:
        test_file /= component
        if test_file.is_symlink():
            return [
                _diagnostic(
                    rule_id="unsafe-suite-path",
                    path=relative_test,
                    message=f"the Appendix C {check_id} path contains a symbolic link",
                    remediation=f"restore {relative_test} as repository-owned regular paths",
                    construct=f"symlink:{check_id}",
                )
            ]

    try:
        resolved_test = test_file.resolve(strict=True)
        resolved_test.relative_to(root)
    except (OSError, ValueError):
        return [
            _diagnostic(
                rule_id="missing-suite",
                path=relative_test,
                message=f"the Appendix C {check_id} test module is missing",
                remediation=f"restore {relative_test}",
                construct=f"missing:{check_id}",
            )
        ]
    if not resolved_test.is_file():
        return [
            _diagnostic(
                rule_id="missing-suite",
                path=relative_test,
                message=f"the Appendix C {check_id} test module is not a regular file",
                remediation=f"restore {relative_test}",
                construct=f"not-file:{check_id}",
            )
        ]

    command = [
        sys.executable,
        "-B",
        "-m",
        "unittest",
        "discover",
        "-s",
        TEST_DIRECTORY,
        "-p",
        filename,
        "-v",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            stdin=subprocess.DEVNULL,
            check=False,
        )
    except OSError as error:
        return [
            _diagnostic(
                rule_id="runner-error",
                path=relative_test,
                message=f"the Appendix C {check_id} suite could not start",
                remediation=f"run {' '.join(command[1:])} from the repository root",
                construct=f"os-error:{type(error).__name__}:{check_id}",
            )
        ]

    if completed.returncode == 0:
        return []
    return [
        _diagnostic(
            rule_id="failure",
            path=relative_test,
            message=f"the Appendix C {check_id} suite failed",
            remediation=f"run {' '.join(command[1:])} from the repository root",
            construct=f"return-code:{completed.returncode}:{check_id}",
        )
    ]


def check_core_suite(context: dict[str, Any]) -> list[dict[str, str]]:
    return _run_suite(
        context, filename="test_core_patterns.py", check_id="core-suite"
    )


def check_network_suite(context: dict[str, Any]) -> list[dict[str, str]]:
    return _run_suite(
        context, filename="test_network_patterns.py", check_id="network-suite"
    )


def register(registry: Any) -> None:
    registry.add(
        plugin_id=PLUGIN_ID,
        api_version=API_VERSION,
        checks={
            "core-suite": check_core_suite,
            "network-suite": check_network_suite,
        },
        prerequisites=(),
        timeout=30,
    )
