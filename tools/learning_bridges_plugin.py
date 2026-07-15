#!/usr/bin/env python3
"""Explicit bounded evidence for the core learning bridges.

The generic Markdown validator remains domain-neutral.  This opt-in plugin
checks the disposable Chapter 1/2/7 observations and delegates executable
authority to the Chapter 26, Chapter 27, and Chapter 28 verifiers.  It never
installs a checker or build tool and never writes inside the repository.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Final, Sequence


PLUGIN_ID: Final = "learning"
API_VERSION: Final = 1
TIMEOUT_SECONDS: Final = 25
OUTPUT_LIMIT_BYTES: Final = 64 * 1024


def _diagnostic(
    path: str,
    rule: str,
    message: str,
    remediation: str,
    *,
    construct: str,
    severity: str | None = None,
) -> dict[str, str]:
    result = {
        "rule_id": rule,
        "path": path,
        "message": message,
        "remediation": remediation,
        "construct": construct,
    }
    if severity is not None:
        result["severity"] = severity
    return result


def _environment(temp: Path) -> dict[str, str]:
    environment = {
        "HOME": str(temp / "home"),
        "NO_COLOR": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TEMP": str(temp / "tmp"),
        "TMP": str(temp / "tmp"),
        "TMPDIR": str(temp / "tmp"),
        "XDG_CACHE_HOME": str(temp / "cache"),
    }
    for path in (temp / "home", temp / "tmp", temp / "cache"):
        path.mkdir(parents=True, exist_ok=True)
    for name in ("PATH", "SYSTEMROOT", "WINDIR"):
        if name in os.environ:
            environment[name] = os.environ[name]
    return environment


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout: int = 8,
) -> tuple[int, bytes, bytes] | None:
    try:
        completed = subprocess.run(
            list(command),
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None
    stdout = completed.stdout[: OUTPUT_LIMIT_BYTES + 1]
    stderr = completed.stderr[: OUTPUT_LIMIT_BYTES + 1]
    if len(stdout) > OUTPUT_LIMIT_BYTES or len(stderr) > OUTPUT_LIMIT_BYTES:
        return completed.returncode, b"<output-limit>", b"<output-limit>"
    return completed.returncode, stdout, stderr


def _early_bridge_contract(temp: Path) -> list[dict[str, str]]:
    """Exercise normal/error/recovery paths in an isolated learner folder."""

    findings: list[dict[str, str]] = []
    environment = _environment(temp)

    hello = temp / "folder with spaces" / "hello.py"
    hello.parent.mkdir(parents=True)
    hello.write_text('print("Hello, Python!")\n', encoding="utf-8")
    normal = _run(
        [sys.executable, "-I", "-B", str(hello)],
        cwd=temp,
        environment=environment,
    )
    if normal is None or normal[:2] != (0, b"Hello, Python!\n"):
        findings.append(
            _diagnostic(
                "chapter-01-introduction/README.md",
                "first-program",
                "the isolated first-program observation did not match its exact output",
                "restore the bounded save/run contract and its successful recovery",
                construct="hello-normal",
            )
        )

    hello.write_text('pritn("Hello, Python!")\n', encoding="utf-8")
    failed = _run(
        [sys.executable, "-I", "-B", str(hello)],
        cwd=temp,
        environment=environment,
    )
    if failed is None or failed[0] == 0 or b"NameError" not in failed[2]:
        findings.append(
            _diagnostic(
                "chapter-01-introduction/README.md",
                "first-traceback",
                "the deliberate first-program failure did not expose NameError",
                "keep the expected `pritn` failure and successful `print` repair",
                construct="hello-name-error",
            )
        )

    scalar = _run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            "calculated=0.1+0.2; print(None is None); print(3<5); "
            "print(calculated==0.3); print(abs(calculated-0.3)<=0.000_000_001)",
        ],
        cwd=temp,
        environment=environment,
    )
    if scalar is None or scalar[:2] != (0, b"True\nTrue\nFalse\nTrue\n"):
        findings.append(
            _diagnostic(
                "chapter-02-variables/README.md",
                "scalar-observation",
                "the truth, absence, or tolerance observation changed",
                "restore the four prerequisite-free scalar observations",
                construct="scalar-normal",
            )
        )

    incompatible = _run(
        [sys.executable, "-I", "-B", "-c", 'print(3 < "5")'],
        cwd=temp,
        environment=environment,
    )
    if incompatible is None or incompatible[0] == 0 or b"TypeError" not in incompatible[2]:
        findings.append(
            _diagnostic(
                "chapter-02-variables/README.md",
                "scalar-type-error",
                "the incompatible ordered comparison did not expose TypeError",
                "restore the expected error and compatible-type recovery",
                construct="scalar-type-error",
            )
        )

    queue_demo = temp / "queue_demo.py"
    queue_demo.write_text(
        'from collections import deque\nprint(deque(["A", "B"]).popleft())\n',
        encoding="utf-8",
    )
    for label, command in (
        ("queue-path", [sys.executable, "-B", str(queue_demo)]),
        ("queue-module", [sys.executable, "-B", "-m", "queue_demo"]),
    ):
        observed = _run(command, cwd=temp, environment=environment)
        if observed is None or observed[:2] != (0, b"A\n"):
            findings.append(
                _diagnostic(
                    "chapter-07-queues/README.md",
                    "local-module",
                    "the local queue module did not produce the same result in both execution forms",
                    "restore the path and `-m` queue_demo contract",
                    construct=label,
                )
            )

    missing = _run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            "import course_module_that_does_not_exist",
        ],
        cwd=temp,
        environment=environment,
    )
    if missing is None or missing[0] == 0 or b"ModuleNotFoundError" not in missing[2]:
        findings.append(
            _diagnostic(
                "chapter-07-queues/README.md",
                "missing-module",
                "the invented module did not expose ModuleNotFoundError",
                "restore the expected missing-module diagnostic contract",
                construct="module-not-found",
            )
        )

    shadow = temp / "collections.py"
    shadow.write_text("# learner-owned shadow module\n", encoding="utf-8")
    shadowed = _run(
        [sys.executable, "-S", "-B", str(queue_demo)],
        cwd=temp,
        environment=environment,
    )
    shadow.rename(temp / "queue_notes.py")
    recovered = _run(
        [sys.executable, "-S", "-B", str(queue_demo)],
        cwd=temp,
        environment=environment,
    )
    if shadowed is None or shadowed[0] == 0 or recovered is None or recovered[:2] != (0, b"A\n"):
        findings.append(
            _diagnostic(
                "chapter-07-queues/README.md",
                "shadow-recovery",
                "learner-owned module shadowing was not detected and repaired in a fresh process",
                "rename only the disposable conflicting source and rerun the standard-library import",
                construct="collections-shadow",
            )
        )

    return findings


def _delegated_contract(
    root: Path,
    temp: Path,
    environment: dict[str, str],
    *,
    command: Sequence[str],
    owner_path: str,
    phase: str,
    prerequisite_exit: int | None = None,
) -> list[dict[str, str]]:
    observed = _run(
        command,
        cwd=root,
        environment=environment,
        timeout=TIMEOUT_SECONDS,
    )
    if observed is None:
        return [
            _diagnostic(
                owner_path,
                "timeout",
                f"the {phase} evidence exceeded {TIMEOUT_SECONDS} seconds",
                "inspect finite bounds, child cleanup, and the narrow verifier",
                construct=f"{phase}-timeout",
            )
        ]
    returncode, stdout, stderr = observed
    if stdout == b"<output-limit>" or stderr == b"<output-limit>":
        return [
            _diagnostic(
                owner_path,
                "output-limit",
                f"the {phase} evidence exceeded the bounded output allowance",
                "reduce verifier output and keep diagnostics focused",
                construct=f"{phase}-output-limit",
            )
        ]
    if prerequisite_exit is not None and returncode == prerequisite_exit:
        return [
            _diagnostic(
                owner_path,
                "prerequisite",
                f"the explicitly selected {phase} prerequisite is unavailable",
                "provision the exact declared development-tool pin; the plugin never installs it implicitly",
                construct=f"{phase}-prerequisite",
                severity="info",
            )
        ]
    if returncode != 0:
        return [
            _diagnostic(
                owner_path,
                "failure",
                f"the bounded {phase} evidence failed",
                "run the documented narrow verifier and repair the first failing contract",
                construct=f"{phase}-exit-{returncode}",
            )
        ]
    return []


def check_contract(context: dict[str, Any]) -> list[dict[str, str]]:
    root = Path(context["root"])
    required = (
        "chapter-26-iteration-generators/examples/iteration_pipeline.py",
        "chapter-26-iteration-generators/examples/tests/test_iteration_pipeline.py",
        "chapter-27-python-typing/examples/typed_inventory.py",
        "chapter-27-python-typing/examples/checker_positive.py",
        "chapter-27-python-typing/examples/checker_negative.py",
        "chapter-27-python-typing/examples/checker_corrected.py",
        "chapter-27-python-typing/requirements-dev.lock",
        "chapter-27-python-typing/tools/verify.py",
        "chapter-28-professional-capstone/examples/order-tracker/BUILD_INPUTS.md",
        "chapter-28-professional-capstone/examples/order-tracker/LICENSE",
        "chapter-28-professional-capstone/examples/order-tracker/MANIFEST.in",
        "chapter-28-professional-capstone/examples/order-tracker/README.md",
        "chapter-28-professional-capstone/examples/order-tracker/pyproject.toml",
        "chapter-28-professional-capstone/examples/order-tracker/requirements-build.txt",
        "chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/cli.py",
        "chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/domain.py",
        "chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/loopback.py",
        "chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/repositories.py",
        "chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/service.py",
        "chapter-28-professional-capstone/examples/order-tracker/tests/test_artifact_verifier.py",
        "chapter-28-professional-capstone/examples/order-tracker/tests/test_cli.py",
        "chapter-28-professional-capstone/examples/order-tracker/tests/test_domain.py",
        "chapter-28-professional-capstone/examples/order-tracker/tests/test_loopback.py",
        "chapter-28-professional-capstone/examples/order-tracker/tests/test_metadata.py",
        "chapter-28-professional-capstone/examples/order-tracker/tests/test_repository_contract.py",
        "chapter-28-professional-capstone/examples/order-tracker/tests/test_service.py",
        "chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py",
    )
    findings: list[dict[str, str]] = []
    for relative in required:
        candidate = root / relative
        if not candidate.is_file() or candidate.is_symlink():
            findings.append(
                _diagnostic(
                    relative,
                    "missing-source",
                    "a required learning-bridges companion input is missing or unsafe",
                    "restore the reviewed companion source before selecting the plugin",
                    construct=relative,
                )
            )
    if findings:
        return findings

    with tempfile.TemporaryDirectory(prefix="learning-bridges-") as raw_temp:
        temp = Path(raw_temp)
        environment = _environment(temp)
        findings.extend(_early_bridge_contract(temp / "early"))
        findings.extend(
            _delegated_contract(
                root,
                temp,
                environment,
                command=(
                    sys.executable,
                    "-I",
                    "-B",
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    "chapter-26-iteration-generators/examples/tests",
                    "-t",
                    "chapter-26-iteration-generators/examples",
                    "-p",
                    "test_*.py",
                ),
                owner_path="chapter-26-iteration-generators/examples/tests",
                phase="chapter-26 companion",
            )
        )
        findings.extend(
            _delegated_contract(
                root,
                temp,
                environment,
                command=(
                    sys.executable,
                    "-I",
                    "-B",
                    "chapter-27-python-typing/tools/verify.py",
                    "--runtime",
                ),
                owner_path="chapter-27-python-typing/tools/verify.py",
                phase="chapter-27 runtime",
            )
        )
        findings.extend(
            _delegated_contract(
                root,
                temp,
                environment,
                command=(
                    sys.executable,
                    "-I",
                    "-B",
                    "chapter-27-python-typing/tools/verify.py",
                    "--checker",
                ),
                owner_path="chapter-27-python-typing/requirements-dev.lock",
                phase="chapter-27 checker",
                prerequisite_exit=2,
            )
        )
        findings.extend(
            _delegated_contract(
                root,
                temp,
                environment,
                command=(
                    sys.executable,
                    "-I",
                    "-B",
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    "chapter-28-professional-capstone/examples/order-tracker/tests",
                    "-t",
                    "chapter-28-professional-capstone/examples/order-tracker",
                    "-p",
                    "test_*.py",
                ),
                owner_path="chapter-28-professional-capstone/examples/order-tracker/tests",
                phase="chapter-28 source",
            )
        )
        findings.extend(
            _delegated_contract(
                root,
                temp,
                environment,
                command=(
                    sys.executable,
                    "-I",
                    "-B",
                    "chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py",
                ),
                owner_path="chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py",
                phase="chapter-28 artifact",
                prerequisite_exit=3,
            )
        )
    return findings


def register(registry: Any) -> None:
    registry.add(
        plugin_id=PLUGIN_ID,
        api_version=API_VERSION,
        checks={"contract": check_contract},
        prerequisites=(),
        timeout=30,
    )
