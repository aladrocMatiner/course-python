"""Domain-only adapter for the repository book quality gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


def _network_suite(context: dict[str, Any]) -> list[dict[str, object]]:
    root = Path(context["root"])
    tests = root / "chapter-23-network-programming" / "examples" / "tests"
    try:
        completed = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(tests), "-v"],
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=25,
            check=False,
            env={"PATH": "", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"},
        )
    except subprocess.TimeoutExpired:
        return [
            {
                "rule_id": "timeout",
                "path": "chapter-23-network-programming/examples/tests",
                "message": "bounded localhost network tests exceeded 25 seconds",
                "remediation": "inspect lifecycle cleanup and deterministic coordination",
                "construct": "network-suite-timeout",
            }
        ]
    if completed.returncode == 0:
        return []
    return [
        {
            "rule_id": "failure",
            "path": "chapter-23-network-programming/examples/tests",
            "message": "the chapter 23 localhost network suite failed",
            "remediation": "run python -B -m unittest discover -s chapter-23-network-programming/examples/tests -v",
            "construct": f"return-code:{completed.returncode}",
        }
    ]


def register(registry: Any) -> None:
    registry.add(
        plugin_id="network",
        api_version=1,
        checks={"network-suite": _network_suite},
        prerequisites=(),
        timeout=30,
    )
