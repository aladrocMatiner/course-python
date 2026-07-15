#!/usr/bin/env python3
"""Run explicit repository quality profiles and emit bounded truthful evidence.

This runner executes trusted repository checks.  It reduces accidental writes and
runaway children; it is not a sandbox for hostile code and it never approves a
human review gate.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import re
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence


MATRIX_SCHEMA_VERSION = 1
REPORT_SCHEMA_VERSION = 1
MAX_TIMEOUT_SECONDS = 600
MAX_OUTPUT_LIMIT_BYTES = 4 * 1024 * 1024
MAX_SNAPSHOT_LIMIT_BYTES = 512 * 1024 * 1024
MATRIX_FILE = "tools/quality_matrix.toml"
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
PREREQUISITE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]*$")
REVISION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$")
ANSI_ESCAPE_RE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|[@-_])")
PUBLIC_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
MESSAGE_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
TOKEN_RE = re.compile(
    r"(?ix)\b(?:"
    r"ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|"
    r"(?:OPENAI_API_KEY|token|secret|password|api[_-]?key)\b\s*[:=]\s*"
    r"(?:\"[^\"\r\n]*\"|'[^'\r\n]*'|[^\s,;|]+)"
    r")"
)
# Public diagnostics deliberately over-redact absolute paths. Spaces are valid
# in all three path families, so punctuation/quotes—not whitespace—bound them.
UNC_PATH_RE = re.compile(
    r"(?<![\\/])(?:\\\\|//)[^\\/\r\n,;|\"']+[\\/][^\r\n,;|\"']+"
)
WINDOWS_DRIVE_PATH_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/][^\r\n,;|\"']+"
)
ABSOLUTE_PATH_RE = re.compile(r"(?<![\w.])/(?!/)[^\r\n,;|\"']+")
ADAPTERS = {
    "tool-unittest",
    "curriculum",
    "parity",
    "publication-signoff",
    "book",
    "book-plugin",
    "openspec-strict",
    "git-whitespace",
}
STATUSES = {"pass", "fail", "error", "unsupported", "not-selected"}
TOP_LEVEL_KEYS = {
    "schema_version",
    "report_schema_version",
    "hard_timeout_seconds",
    "hard_output_limit_bytes",
    "snapshot_limit_bytes",
    "evidence_scope",
    "human_review_boundary",
    "checks",
    "profiles",
}
COMMON_CHECK_KEYS = {
    "id",
    "adapter",
    "timeout_seconds",
    "output_limit_bytes",
    "prerequisites",
    "evidence_scope",
}
REQUIRED_CHECK_CONTRACTS = {
    "tool-tests": ("tool-unittest", None),
    "curriculum": ("curriculum", None),
    "parity": ("parity", None),
    "book-generic": ("book", None),
    "learning-bridges": (
        "book-plugin",
        "tools/learning_bridges_plugin.py",
    ),
    "network-domain": (
        "book-plugin",
        "chapter-23-network-programming/tools/bookcheck_plugin.py",
    ),
    "cpp-domain": (
        "book-plugin",
        "chapter-24-python-cpp-integration/tools/bookcheck_plugin.py",
    ),
    "rust-domain": (
        "book-plugin",
        "chapter-25-python-rust-integration/tools/bookcheck_plugin.py",
    ),
    "openspec-strict": ("openspec-strict", None),
    "whitespace": ("git-whitespace", None),
    "publication-signoff": ("publication-signoff", None),
}
REQUIRED_PROFILE_CONTRACTS = {
    "core": ("tool-tests", "curriculum", "parity", "book-generic"),
    "learning-bridges": ("learning-bridges",),
    "network-domain": ("network-domain",),
    "cpp-domain": ("cpp-domain",),
    "rust-domain": ("rust-domain",),
    "handoff": tuple(REQUIRED_CHECK_CONTRACTS),
}
_PR_SET_CHILD_SUBREAPER = 36
_PR_GET_CHILD_SUBREAPER = 37
_SUBREAPER_LOCK = threading.Lock()


class MatrixError(ValueError):
    """The declarative runner contract is malformed or unsafe."""


class RunnerError(RuntimeError):
    """The runner could not establish complete execution evidence."""


@dataclass(frozen=True)
class Check:
    id: str
    adapter: str
    timeout_seconds: int
    output_limit_bytes: int
    prerequisites: tuple[str, ...]
    evidence_scope: str
    plugin_path: str | None = None

    def __post_init__(self) -> None:
        _required_public_text(self.evidence_scope, "check.evidence_scope")


@dataclass(frozen=True)
class Matrix:
    checks: tuple[Check, ...]
    profiles: Mapping[str, tuple[str, ...]]
    hard_timeout_seconds: int
    hard_output_limit_bytes: int
    snapshot_limit_bytes: int
    evidence_scope: str
    human_review_boundary: str

    def __post_init__(self) -> None:
        _required_public_text(self.evidence_scope, "evidence_scope")
        _required_public_text(self.human_review_boundary, "human_review_boundary")

    @property
    def by_id(self) -> dict[str, Check]:
        return {check.id: check for check in self.checks}


@dataclass(frozen=True)
class Result:
    id: str
    adapter: str
    status: str
    evidence_scope: str
    message: str

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"unknown result status: {self.status}")
        try:
            _required_public_text(self.evidence_scope, "result.evidence_scope")
        except MatrixError:
            raise ValueError("result.evidence_scope must be safe public text") from None
        if not isinstance(self.message, str):
            raise ValueError("result.message must be text")
        object.__setattr__(self, "message", sanitize_public_text(self.message))


@dataclass(frozen=True)
class Report:
    evidence_scope: str
    human_review_boundary: str
    selection: str
    selected_checks: tuple[str, ...]
    changed_from: str | None
    revision: str
    repository_tree_sha256: str
    observed_host: Mapping[str, str]
    results: tuple[Result, ...]

    def __post_init__(self) -> None:
        try:
            _required_public_text(self.evidence_scope, "report.evidence_scope")
            _required_public_text(
                self.human_review_boundary, "report.human_review_boundary"
            )
        except MatrixError:
            raise ValueError("report public contract fields must be safe text") from None

    @property
    def overall_status(self) -> str:
        selected = [item for item in self.results if item.status != "not-selected"]
        if any(item.status in {"error", "unsupported"} for item in selected):
            return "error"
        if any(item.status == "fail" for item in selected):
            return "fail"
        return "pass"

    @property
    def exit_code(self) -> int:
        return {"pass": 0, "fail": 1, "error": 2}[self.overall_status]

    def public_dict(self) -> dict[str, object]:
        return {
            "schema_version": REPORT_SCHEMA_VERSION,
            "evidence_scope": self.evidence_scope,
            "human_review_boundary": self.human_review_boundary,
            "overall_status": self.overall_status,
            "selection": {
                "mode": self.selection,
                "checks": list(self.selected_checks),
                "changed_from": self.changed_from,
            },
            "repository": {
                "revision": self.revision,
                "tree_sha256": self.repository_tree_sha256,
            },
            "observed_host": dict(sorted(self.observed_host.items())),
            "results": [asdict(item) for item in self.results],
        }


@dataclass(frozen=True)
class ChildOutcome:
    returncode: int | None
    infrastructure_error: str | None = None
    observed_output_bytes: int = 0


def _strict_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise MatrixError(f"{name} must be an integer")
    return value


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise MatrixError(f"{name} must be a non-empty bounded string")
    return value


def _required_public_text(value: object, name: str) -> str:
    text = _required_text(value, name)
    if (
        text != text.strip()
        or PUBLIC_CONTROL_RE.search(text)
        or ANSI_ESCAPE_RE.search(text)
        or TOKEN_RE.search(text)
        or UNC_PATH_RE.search(text)
        or WINDOWS_DRIVE_PATH_RE.search(text)
        or ABSOLUTE_PATH_RE.search(text)
    ):
        # Never reflect the rejected field: it may itself contain the secret or
        # local path that made the matrix unsafe for public evidence.
        raise MatrixError(f"{name} must be safe single-line public text")
    return text


def safe_relative_path(root: Path, raw: object, name: str) -> str:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise MatrixError(f"{name} must be a repository-relative path")
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise MatrixError(f"{name} escapes the repository")
    root_resolved = root.resolve()
    try:
        (root / relative).resolve(strict=False).relative_to(root_resolved)
    except (OSError, ValueError):
        raise MatrixError(f"{name} escapes the repository") from None
    return relative.as_posix()


def parse_matrix(payload: object, root: Path) -> Matrix:
    if not isinstance(payload, dict):
        raise MatrixError("matrix root must be a table")
    unknown = set(payload) - TOP_LEVEL_KEYS
    if unknown:
        raise MatrixError(f"unknown matrix keys: {', '.join(sorted(unknown))}")
    if payload.get("schema_version") != MATRIX_SCHEMA_VERSION:
        raise MatrixError("unsupported matrix schema_version")
    if payload.get("report_schema_version") != REPORT_SCHEMA_VERSION:
        raise MatrixError("unsupported report_schema_version")

    hard_timeout = _strict_int(payload.get("hard_timeout_seconds"), "hard_timeout_seconds")
    hard_output = _strict_int(payload.get("hard_output_limit_bytes"), "hard_output_limit_bytes")
    snapshot_limit = _strict_int(payload.get("snapshot_limit_bytes"), "snapshot_limit_bytes")
    if not 0 < hard_timeout <= MAX_TIMEOUT_SECONDS:
        raise MatrixError("hard_timeout_seconds is outside the supported maximum")
    if not 0 < hard_output <= MAX_OUTPUT_LIMIT_BYTES:
        raise MatrixError("hard_output_limit_bytes is outside the supported maximum")
    if not 0 < snapshot_limit <= MAX_SNAPSHOT_LIMIT_BYTES:
        raise MatrixError("snapshot_limit_bytes is outside the supported maximum")

    raw_checks = payload.get("checks")
    if not isinstance(raw_checks, list) or not raw_checks:
        raise MatrixError("checks must be a non-empty array of tables")
    checks: list[Check] = []
    seen_ids: set[str] = set()
    for index, raw_check in enumerate(raw_checks):
        if not isinstance(raw_check, dict):
            raise MatrixError(f"checks[{index}] must be a table")
        allowed = set(COMMON_CHECK_KEYS)
        if raw_check.get("adapter") == "book-plugin":
            allowed.add("plugin_path")
        unknown_check = set(raw_check) - allowed
        if unknown_check:
            raise MatrixError(
                f"unknown keys for checks[{index}]: {', '.join(sorted(unknown_check))}"
            )
        check_id = raw_check.get("id")
        if not isinstance(check_id, str) or not ID_RE.fullmatch(check_id):
            raise MatrixError(f"checks[{index}].id is unsafe")
        if check_id in seen_ids:
            raise MatrixError(f"duplicate check id: {check_id}")
        seen_ids.add(check_id)
        adapter = raw_check.get("adapter")
        if adapter not in ADAPTERS:
            raise MatrixError(f"unknown adapter for {check_id}")
        timeout = _strict_int(raw_check.get("timeout_seconds"), f"{check_id}.timeout_seconds")
        output_limit = _strict_int(
            raw_check.get("output_limit_bytes"), f"{check_id}.output_limit_bytes"
        )
        if not 0 < timeout <= hard_timeout:
            raise MatrixError(f"{check_id}.timeout_seconds exceeds the matrix hard bound")
        if not 0 < output_limit <= hard_output:
            raise MatrixError(f"{check_id}.output_limit_bytes exceeds the matrix hard bound")
        raw_prerequisites = raw_check.get("prerequisites")
        if not isinstance(raw_prerequisites, list) or any(
            not isinstance(item, str) or not PREREQUISITE_RE.fullmatch(item)
            for item in raw_prerequisites
        ):
            raise MatrixError(f"{check_id}.prerequisites is invalid")
        if len(set(raw_prerequisites)) != len(raw_prerequisites):
            raise MatrixError(f"{check_id}.prerequisites contains duplicates")
        plugin_path: str | None = None
        if adapter == "book-plugin":
            plugin_path = safe_relative_path(root, raw_check.get("plugin_path"), f"{check_id}.plugin_path")
            if not (root / plugin_path).is_file():
                raise MatrixError(f"{check_id}.plugin_path does not name a file")
        checks.append(
            Check(
                id=check_id,
                adapter=adapter,
                timeout_seconds=timeout,
                output_limit_bytes=output_limit,
                prerequisites=tuple(raw_prerequisites),
                evidence_scope=_required_public_text(
                    raw_check.get("evidence_scope"), f"{check_id}.evidence_scope"
                ),
                plugin_path=plugin_path,
            )
        )

    raw_profiles = payload.get("profiles")
    if not isinstance(raw_profiles, dict) or not raw_profiles:
        raise MatrixError("profiles must be a non-empty table")
    positions = {check.id: index for index, check in enumerate(checks)}
    profiles: dict[str, tuple[str, ...]] = {}
    for profile_id, raw_ids in raw_profiles.items():
        if not isinstance(profile_id, str) or not ID_RE.fullmatch(profile_id):
            raise MatrixError(f"unsafe profile id: {profile_id}")
        if not isinstance(raw_ids, list) or not raw_ids:
            raise MatrixError(f"profile {profile_id} must select checks")
        if any(not isinstance(item, str) or not ID_RE.fullmatch(item) for item in raw_ids):
            raise MatrixError(f"profile {profile_id} contains an unsafe check id")
        if len(set(raw_ids)) != len(raw_ids):
            raise MatrixError(f"profile {profile_id} contains duplicate checks")
        missing = [item for item in raw_ids if item not in positions]
        if missing:
            raise MatrixError(f"profile {profile_id} references unknown checks: {', '.join(missing)}")
        if [positions[item] for item in raw_ids] != sorted(positions[item] for item in raw_ids):
            raise MatrixError(f"profile {profile_id} is not in deterministic matrix order")
        profiles[profile_id] = tuple(raw_ids)

    parsed_by_id = {check.id: check for check in checks}
    for check_id, (adapter, plugin_path) in REQUIRED_CHECK_CONTRACTS.items():
        check = parsed_by_id.get(check_id)
        if check is None:
            raise MatrixError(f"required check is missing: {check_id}")
        if check.adapter != adapter or check.plugin_path != plugin_path:
            raise MatrixError(f"required check contract changed: {check_id}")
    for profile_id, required_ids in REQUIRED_PROFILE_CONTRACTS.items():
        if profiles.get(profile_id) != required_ids:
            raise MatrixError(f"required profile contract changed: {profile_id}")

    return Matrix(
        checks=tuple(checks),
        profiles=profiles,
        hard_timeout_seconds=hard_timeout,
        hard_output_limit_bytes=hard_output,
        snapshot_limit_bytes=snapshot_limit,
        evidence_scope=_required_public_text(payload.get("evidence_scope"), "evidence_scope"),
        human_review_boundary=_required_public_text(
            payload.get("human_review_boundary"), "human_review_boundary"
        ),
    )


def load_matrix(path: Path, root: Path) -> Matrix:
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise MatrixError(f"cannot read matrix: {exc}") from None
    return parse_matrix(payload, root)


def validate_revision(raw: str) -> str:
    if (
        not REVISION_RE.fullmatch(raw)
        or ".." in raw
        or "//" in raw
        or "@{" in raw
        or raw.endswith(("/", "."))
    ):
        raise MatrixError("changed-from must be a safe Git revision")
    return raw


def resolve_selection(
    matrix: Matrix,
    profile: str | None,
    explicit_checks: Sequence[str],
    changed_from: str | None,
) -> tuple[str, tuple[str, ...], str | None]:
    if profile and explicit_checks:
        raise MatrixError("--profile and --check are mutually exclusive")
    if explicit_checks:
        if len(set(explicit_checks)) != len(explicit_checks):
            raise MatrixError("--check cannot select the same check twice")
        unknown = [item for item in explicit_checks if item not in matrix.by_id]
        if unknown:
            raise MatrixError(f"unknown check: {', '.join(unknown)}")
        selected_set = set(explicit_checks)
        selected = tuple(check.id for check in matrix.checks if check.id in selected_set)
        selection = "explicit"
    else:
        profile = profile or "core"
        if profile not in matrix.profiles:
            raise MatrixError(f"unknown profile: {profile}")
        selected = matrix.profiles[profile]
        selection = profile
    normalized_revision = validate_revision(changed_from) if changed_from else None
    if normalized_revision and not any(matrix.by_id[item].adapter == "book" for item in selected):
        raise MatrixError("--changed-from requires selection of generic book validation")
    return selection, selected, normalized_revision


def build_argv(check: Check, changed_from: str | None = None) -> list[str]:
    python = sys.executable
    if check.adapter == "tool-unittest":
        return [python, "-B", "-m", "unittest", "discover", "-s", "tools/tests", "-p", "test_*.py", "-v"]
    if check.adapter == "curriculum":
        return [python, "-B", "tools/validate_curriculum.py", "--json"]
    if check.adapter == "parity":
        return [python, "-B", "tools/parity_review.py"]
    if check.adapter == "publication-signoff":
        return [
            python,
            "-B",
            "tools/parity_review.py",
            "--verify-publication-signoff",
            "tools/publication_signoff.json",
        ]
    if check.adapter == "book":
        argv = [python, "-B", "tools/validate_book.py", "--format", "json"]
        if changed_from:
            argv.extend(["--changed-from", changed_from])
        return argv
    if check.adapter == "book-plugin":
        assert check.plugin_path is not None
        return [
            python,
            "-B",
            "tools/validate_book.py",
            "--format",
            "json",
            "--plugin",
            check.plugin_path,
        ]
    if check.adapter == "openspec-strict":
        return ["openspec", "validate", "--changes", "--strict", "--no-interactive"]
    if check.adapter == "git-whitespace":
        # Compare both the index and worktree with HEAD for a local handoff.
        # PR/push range checks remain owned by the workflow.
        return ["git", "diff", "--check", "HEAD"]
    raise MatrixError(f"adapter is not implemented: {check.adapter}")


def process_tree_supported() -> bool:
    """Return whether Linux subreaper plus /proc tree containment is available."""
    if os.name != "posix" or not sys.platform.startswith("linux") or not Path("/proc/self/stat").is_file():
        return False
    try:
        _get_child_subreaper()
        _observable_parent_map()
    except (AttributeError, OSError, RunnerError, TypeError):
        return False
    return True


def _prctl() -> object:
    library = ctypes.CDLL(None, use_errno=True)
    function = library.prctl
    function.restype = ctypes.c_int
    return function


def _get_child_subreaper() -> int:
    value = ctypes.c_int()
    if _prctl()(_PR_GET_CHILD_SUBREAPER, ctypes.byref(value), 0, 0, 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    return value.value


def _set_child_subreaper(value: int) -> None:
    if _prctl()(_PR_SET_CHILD_SUBREAPER, value, 0, 0, 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def _proc_parent_map() -> dict[int, int]:
    parents: dict[int, int] = {}
    try:
        entries = list(Path("/proc").iterdir())
    except OSError as exc:
        raise RunnerError(f"process observability failed: {exc.__class__.__name__}") from None
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            raw = (entry / "stat").read_text(encoding="utf-8")
            close = raw.rfind(")")
            fields = raw[close + 2 :].split()
            parents[int(entry.name)] = int(fields[1])
        except (FileNotFoundError, ProcessLookupError):
            # A process may disappear normally between listing and reading it.
            continue
        except OSError as exc:
            raise RunnerError(
                f"process observability failed: {exc.__class__.__name__}"
            ) from None
        except (UnicodeError, ValueError, IndexError) as exc:
            raise RunnerError(
                f"process observability failed: malformed proc entry ({exc.__class__.__name__})"
            ) from None
    return parents


def _observable_parent_map() -> dict[int, int]:
    parents = _proc_parent_map()
    if os.getpid() not in parents:
        raise RunnerError("process observability failed: current PID is absent from /proc")
    return parents


def _descendant_closure(seeds: set[int], parents: Mapping[int, int]) -> set[int]:
    descendants: set[int] = set()
    frontier = set(seeds)
    while frontier:
        children = {
            pid for pid, parent in parents.items() if parent in frontier and pid not in descendants
        }
        descendants.update(children)
        frontier = children
    return descendants


def _reap_known_children(known: set[int]) -> None:
    for pid in tuple(known):
        try:
            waited, _ = os.waitpid(pid, os.WNOHANG)
        except (ChildProcessError, OSError):
            continue
        if waited == pid:
            known.discard(pid)


def _owned_processes(direct_pid: int, baseline_children: set[int], known: set[int]) -> set[int]:
    _reap_known_children(known)
    parents = _observable_parent_map()
    if direct_pid not in parents and _pid_alive(direct_pid):
        raise RunnerError(
            "process observability failed: live direct child is absent from /proc map"
        )
    missing_known = known.difference(parents)
    if any(_pid_alive(pid) for pid in missing_known):
        # Keep every observed PID available to the no-/proc cleanup fallback.
        raise RunnerError(
            "process observability failed: live known descendant is absent from /proc map"
        )
    known.difference_update(missing_known)
    known.update(_descendant_closure({direct_pid}, parents))
    adopted = {
        pid
        for pid, parent in parents.items()
        if parent == os.getpid() and pid not in baseline_children and pid != direct_pid
    }
    known.update(adopted)
    known.update(_descendant_closure(set(known), parents))
    return set(known)


def _signal_processes(pids: set[int], chosen_signal: int) -> None:
    for pid in sorted(pids, reverse=True):
        try:
            os.kill(pid, chosen_signal)
        except ProcessLookupError:
            pass
        except PermissionError:
            # Keep the PID visible so containment fails closed below.
            continue


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _terminate_known_without_proc(
    process: subprocess.Popen[bytes], known: set[int]
) -> bool:
    """Freeze and kill only PIDs observed before /proc became unavailable."""
    targets = {pid for pid in known if _pid_alive(pid)}
    if process.poll() is None:
        targets.add(process.pid)
    # Stop known processes first so they cannot fork between fallback scans.
    _signal_processes(targets, signal.SIGSTOP)
    _signal_processes(targets, signal.SIGKILL)
    if process.poll() is None:
        try:
            process.wait(timeout=0.5)
        except subprocess.TimeoutExpired:
            return False
    deadline = time.monotonic() + 0.5
    stable_empty = 0
    while time.monotonic() < deadline:
        _reap_known_children(known)
        alive = {pid for pid in known if _pid_alive(pid)}
        if alive:
            stable_empty = 0
            _signal_processes(alive, signal.SIGKILL)
        else:
            stable_empty += 1
            if stable_empty >= 3:
                return True
        time.sleep(0.01)
    return False


def _terminate_owned_tree(
    process: subprocess.Popen[bytes], baseline_children: set[int], known: set[int]
) -> tuple[bool, bool]:
    """Terminate direct/adopted descendants, including children that call setsid()."""
    # Stop already observed PIDs before the next /proc scan. Once execution
    # evidence is invalid, a graceful running window would let a process
    # handle or ignore SIGTERM, fork, or mutate the checkout before SIGKILL.
    frozen = {pid for pid in known if _pid_alive(pid)}
    if process.poll() is None:
        frozen.add(process.pid)
    _signal_processes(frozen, signal.SIGSTOP)

    freeze_deadline = time.monotonic() + 0.3
    stable_frozen_rounds = 0
    while time.monotonic() < freeze_deadline:
        try:
            owned = _owned_processes(process.pid, baseline_children, known)
        except RunnerError:
            return _terminate_known_without_proc(process, known), False
        targets = set(owned)
        if process.poll() is None:
            targets.add(process.pid)
        new_targets = targets.difference(frozen)
        if targets:
            _signal_processes(targets, signal.SIGSTOP)
        frozen.update(targets)
        if new_targets:
            stable_frozen_rounds = 0
        else:
            stable_frozen_rounds += 1
            if stable_frozen_rounds >= 3:
                break
        time.sleep(0.01)

    # Do not resume a stopped process to deliver a graceful signal: its signal
    # handling is untrusted cleanup behavior after an infrastructure
    # failure. SIGKILL is the only signal that is both immediate and
    # uncatchable here.
    _signal_processes(frozen, signal.SIGKILL)
    if process.poll() is None:
        try:
            process.wait(timeout=0.2)
        except subprocess.TimeoutExpired:
            return False, True
    stable_empty = 0
    deadline = time.monotonic() + 0.5
    while time.monotonic() < deadline:
        try:
            owned = _owned_processes(process.pid, baseline_children, known)
        except RunnerError:
            return _terminate_known_without_proc(process, known), False
        targets = set(owned)
        if process.poll() is None:
            targets.add(process.pid)
        if targets:
            stable_empty = 0
            _signal_processes(targets, signal.SIGSTOP)
            _signal_processes(targets, signal.SIGKILL)
        else:
            stable_empty += 1
            if stable_empty >= 3:
                return True, True
        time.sleep(0.01)
    return False, True


def _trusted_temp_parent(root: Path) -> Path:
    root_resolved = root.resolve()
    for raw in ("/tmp", "/var/tmp"):
        candidate = Path(raw).resolve()
        try:
            candidate.relative_to(root_resolved)
        except ValueError:
            pass
        else:
            continue
        if candidate.is_dir() and os.access(candidate, os.W_OK | os.X_OK):
            return candidate
    raise RunnerError("no trusted temporary directory exists outside the repository")


def _minimal_environment(temporary: Path) -> dict[str, str]:
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(temporary / "home"),
        "TMPDIR": str(temporary),
        "TMP": str(temporary),
        "TEMP": str(temporary),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "NO_COLOR": "1",
        "GIT_CONFIG_NOSYSTEM": "1",
        "LC_ALL": "C",
        "LANG": "C",
        "TZ": "UTC",
    }
    for name in ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT"):
        if name in os.environ:
            environment[name] = os.environ[name]
    return environment


def _run_child_under_subreaper(
    root: Path,
    argv: Sequence[str],
    timeout_seconds: int,
    output_limit_bytes: int,
    temporary_parent: Path,
) -> ChildOutcome:
    try:
        initial_parents = _observable_parent_map()
    except RunnerError as exc:
        return ChildOutcome(None, str(exc))
    baseline_children = {
        pid for pid, parent in initial_parents.items() if parent == os.getpid()
    }
    process: subprocess.Popen[bytes] | None = None
    known_descendants: set[int] = set()
    observed_output = 0
    try:
        with tempfile.TemporaryDirectory(
            prefix="course-quality-run-", dir=temporary_parent
        ) as raw_temp:
            temporary = Path(raw_temp)
            (temporary / "home").mkdir()
            try:
                process = subprocess.Popen(
                    list(argv),
                    cwd=root,
                    env=_minimal_environment(temporary),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=False,
                    start_new_session=True,
                )
            except OSError as exc:
                return ChildOutcome(None, f"child could not start: {exc.__class__.__name__}")
            assert process.stdout is not None
            os.set_blocking(process.stdout.fileno(), False)
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)
            output_eof = False
            started = time.monotonic()
            direct_done_at: float | None = None
            infrastructure_error: str | None = None
            observability_lost = False
            try:
                while True:
                    for key, _ in selector.select(timeout=0.01):
                        while True:
                            remaining = output_limit_bytes - observed_output
                            read_size = min(65536, max(1, remaining + 1))
                            try:
                                chunk = os.read(key.fd, read_size)
                            except BlockingIOError:
                                break
                            if not chunk:
                                output_eof = True
                                try:
                                    selector.unregister(process.stdout)
                                except KeyError:
                                    pass
                                break
                            retained = min(len(chunk), max(0, remaining))
                            observed_output += retained
                            if retained != len(chunk):
                                infrastructure_error = "child output exceeded the configured bound"
                                break
                        if infrastructure_error:
                            break

                    owned = _owned_processes(
                        process.pid, baseline_children, known_descendants
                    )
                    returncode = process.poll()
                    now = time.monotonic()
                    if infrastructure_error:
                        break
                    if now - started > timeout_seconds:
                        infrastructure_error = "child exceeded the configured timeout"
                        break
                    if returncode is None:
                        continue
                    if direct_done_at is None:
                        direct_done_at = now
                    if owned:
                        infrastructure_error = "child left a surviving descendant"
                        break
                    # Require a short quiescent window after direct exit so an
                    # orphan cannot race /proc adoption and close its pipe first.
                    if output_eof and now - direct_done_at >= 0.05:
                        break
                    if now - direct_done_at > 0.15:
                        infrastructure_error = "child left a surviving descendant"
                        break
            except RunnerError as exc:
                observability_lost = True
                infrastructure_error = str(exc)
            except Exception as exc:  # Monitoring failures are infrastructure failures.
                infrastructure_error = f"child monitoring failed: {exc.__class__.__name__}"
            finally:
                selector.close()
                process.stdout.close()

            if infrastructure_error:
                contained, observable_cleanup = _terminate_owned_tree(
                    process, baseline_children, known_descendants
                )
                if not contained:
                    infrastructure_error += "; known descendant cleanup did not converge"
                if observability_lost or not observable_cleanup:
                    infrastructure_error += (
                        "; process observability was lost; cleanup of unobserved "
                        "descendants cannot be proven"
                    )
                return ChildOutcome(None, infrastructure_error, observed_output)
            return ChildOutcome(process.wait(), None, observed_output)
    except OSError as exc:
        return ChildOutcome(
            None, f"temporary execution failed: {exc.__class__.__name__}", observed_output
        )
    finally:
        if process is not None and process.poll() is None:
            _terminate_owned_tree(process, baseline_children, known_descendants)


def run_child(
    root: Path,
    argv: Sequence[str],
    timeout_seconds: int,
    output_limit_bytes: int,
) -> ChildOutcome:
    if not process_tree_supported():
        return ChildOutcome(None, "Linux subreaper process-tree cleanup is unavailable on this host")
    try:
        temporary_parent = _trusted_temp_parent(root)
    except RunnerError as exc:
        return ChildOutcome(None, str(exc))

    with _SUBREAPER_LOCK:
        try:
            previous_subreaper = _get_child_subreaper()
            _set_child_subreaper(1)
        except (AttributeError, OSError, TypeError) as exc:
            return ChildOutcome(None, f"Linux subreaper setup failed: {exc.__class__.__name__}")
        try:
            try:
                outcome = _run_child_under_subreaper(
                    root, argv, timeout_seconds, output_limit_bytes, temporary_parent
                )
            except Exception as exc:
                outcome = ChildOutcome(
                    None, f"child containment failed: {exc.__class__.__name__}"
                )
        finally:
            try:
                _set_child_subreaper(previous_subreaper)
                restore_error: str | None = None
            except (AttributeError, OSError, TypeError) as exc:
                restore_error = f"Linux subreaper restoration failed: {exc.__class__.__name__}"
        if restore_error:
            return ChildOutcome(None, restore_error, outcome.observed_output_bytes)
        return outcome


def snapshot_repository(root: Path, limit_bytes: int) -> dict[str, str]:
    """Hash publishable tree entries for mutation detection.

    The snapshot includes tracked and untracked regular files (including empty
    files), symlinks, and special files. It excludes `.git` metadata and cannot
    represent empty directories or directory modes; Git cannot publish an empty
    directory either. This detects accidental source-tree writes and is not a
    hostile-code filesystem sandbox.
    """
    snapshot: dict[str, str] = {}
    consumed = 0

    def record(path: Path) -> None:
        nonlocal consumed
        relative = path.relative_to(root).as_posix()
        try:
            metadata = path.lstat()
            mode = stat.S_IMODE(metadata.st_mode)
            if stat.S_ISLNK(metadata.st_mode):
                raw = os.readlink(path).encode("utf-8", "surrogateescape")
                kind = "link"
            elif stat.S_ISREG(metadata.st_mode):
                raw_hash = hashlib.sha256()
                size = 0
                with path.open("rb") as stream:
                    while chunk := stream.read(1024 * 1024):
                        size += len(chunk)
                        consumed += len(chunk)
                        if consumed > limit_bytes:
                            raise RunnerError("repository snapshot exceeds the configured bound")
                        raw_hash.update(chunk)
                snapshot[relative] = f"file:{mode:o}:{size}:{raw_hash.hexdigest()}"
                return
            else:
                raw = f"{metadata.st_mode}:{metadata.st_rdev}".encode()
                kind = "special"
            consumed += len(raw)
            if consumed > limit_bytes:
                raise RunnerError("repository snapshot exceeds the configured bound")
            snapshot[relative] = f"{kind}:{mode:o}:{hashlib.sha256(raw).hexdigest()}"
        except RunnerError:
            raise
        except OSError as exc:
            raise RunnerError(f"repository snapshot failed at {relative}: {exc.__class__.__name__}") from None

    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(item for item in directories if item != ".git")
        for directory in tuple(directories):
            candidate = current_path / directory
            if candidate.is_symlink():
                record(candidate)
                directories.remove(directory)
        for filename in sorted(files):
            record(current_path / filename)
    return dict(sorted(snapshot.items()))


def snapshot_digest(snapshot: Mapping[str, str]) -> str:
    digest = hashlib.sha256()
    for path, value in sorted(snapshot.items()):
        digest.update(path.encode("utf-8", "surrogateescape"))
        digest.update(b"\0")
        digest.update(value.encode())
        digest.update(b"\n")
    return digest.hexdigest()


def snapshot_changes(before: Mapping[str, str], after: Mapping[str, str]) -> tuple[str, ...]:
    return tuple(
        path
        for path in sorted(set(before) | set(after))
        if before.get(path) != after.get(path)
    )


def sanitize_public_text(message: str) -> str:
    """Return bounded single-line diagnostics without secrets or local paths."""
    safe = ANSI_ESCAPE_RE.sub("", message)
    safe = TOKEN_RE.sub("<redacted>", safe)
    safe = UNC_PATH_RE.sub("<path>", safe)
    safe = WINDOWS_DRIVE_PATH_RE.sub("<path>", safe)
    safe = ABSOLUTE_PATH_RE.sub("<path>", safe)
    safe = MESSAGE_CONTROL_RE.sub(" ", safe)
    safe = " ".join(safe.split())
    return safe[:512] or "runner evidence is unavailable"


def sanitize_message(message: str, root: Path) -> str:
    safe = message.replace(str(root.resolve()), "<repo>")
    try:
        safe = safe.replace(str(Path.home()), "<home>")
    except RuntimeError:
        pass
    return sanitize_public_text(safe)


def _prerequisite_available(name: str) -> bool:
    return shutil.which(name, path=os.environ.get("PATH", "")) is not None


def execute_check(
    root: Path,
    matrix: Matrix,
    check: Check,
    changed_from: str | None,
    *,
    child_runner: Callable[[Path, Sequence[str], int, int], ChildOutcome] = run_child,
    prerequisite_available: Callable[[str], bool] = _prerequisite_available,
) -> tuple[Result, bool]:
    missing = [name for name in check.prerequisites if not prerequisite_available(name)]
    if missing:
        return (
            Result(
                check.id,
                check.adapter,
                "unsupported",
                check.evidence_scope,
                f"missing declared prerequisite: {', '.join(missing)}",
            ),
            False,
        )
    if not process_tree_supported():
        return (
            Result(
                check.id,
                check.adapter,
                "unsupported",
                check.evidence_scope,
                "tested process-tree cleanup is unavailable on this host",
            ),
            False,
        )
    try:
        before = snapshot_repository(root, matrix.snapshot_limit_bytes)
        outcome = child_runner(
            root,
            build_argv(check, changed_from if check.adapter == "book" else None),
            check.timeout_seconds,
            check.output_limit_bytes,
        )
        after = snapshot_repository(root, matrix.snapshot_limit_bytes)
    except (MatrixError, RunnerError) as exc:
        return (
            Result(
                check.id,
                check.adapter,
                "error",
                check.evidence_scope,
                sanitize_message(str(exc), root),
            ),
            True,
        )
    changed = snapshot_changes(before, after)
    if changed:
        visible = ", ".join(changed[:3])
        if len(changed) > 3:
            visible += f", and {len(changed) - 3} more"
        return (
            Result(
                check.id,
                check.adapter,
                "error",
                check.evidence_scope,
                sanitize_message(f"repository mutation detected: {visible}", root),
            ),
            True,
        )
    if outcome.infrastructure_error:
        return (
            Result(
                check.id,
                check.adapter,
                "error",
                check.evidence_scope,
                sanitize_message(outcome.infrastructure_error, root),
            ),
            False,
        )
    if outcome.returncode == 0:
        status, message = "pass", "check completed successfully on the observed host"
    elif outcome.returncode == 1:
        status, message = "fail", "quality check reported findings; run the direct owner command for details"
    else:
        status, message = "error", "quality owner returned a configuration or execution error"
    return Result(check.id, check.adapter, status, check.evidence_scope, message), False


def observed_revision(root: Path) -> str:
    git = shutil.which("git", path=os.environ.get("PATH", ""))
    if not git:
        return "unavailable"
    try:
        completed = subprocess.run(
            [git, "rev-parse", "--verify", "HEAD"],
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=2,
            check=False,
            env={"PATH": os.environ.get("PATH", ""), "LC_ALL": "C"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    value = completed.stdout.decode("ascii", "ignore").strip()
    return value if completed.returncode == 0 and re.fullmatch(r"[0-9a-fA-F]{7,64}", value) else "unavailable"


def run_quality(
    root: Path,
    matrix: Matrix,
    selection: str,
    selected_ids: Sequence[str],
    changed_from: str | None,
    *,
    child_runner: Callable[[Path, Sequence[str], int, int], ChildOutcome] = run_child,
    prerequisite_available: Callable[[str], bool] = _prerequisite_available,
) -> Report:
    initial = snapshot_repository(root, matrix.snapshot_limit_bytes)
    selected = set(selected_ids)
    results: list[Result] = []
    mutation_blocked = False
    for check in matrix.checks:
        if check.id not in selected:
            results.append(
                Result(
                    check.id,
                    check.adapter,
                    "not-selected",
                    check.evidence_scope,
                    "check was not selected and did not run",
                )
            )
            continue
        if mutation_blocked:
            results.append(
                Result(
                    check.id,
                    check.adapter,
                    "error",
                    check.evidence_scope,
                    "check did not run after an earlier repository mutation",
                )
            )
            continue
        result, mutation_blocked = execute_check(
            root,
            matrix,
            check,
            changed_from,
            child_runner=child_runner,
            prerequisite_available=prerequisite_available,
        )
        results.append(result)
    return Report(
        evidence_scope=matrix.evidence_scope,
        human_review_boundary=matrix.human_review_boundary,
        selection=selection,
        selected_checks=tuple(selected_ids),
        changed_from=changed_from,
        revision=observed_revision(root),
        repository_tree_sha256=snapshot_digest(initial),
        observed_host={
            "architecture": platform.machine() or "unknown",
            "operating_system": platform.system() or sys.platform,
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "scope": "observed host only",
        },
        results=tuple(results),
    )


def render_json(report: Report) -> str:
    return json.dumps(report.public_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_text(report: Report) -> str:
    lines = [
        f"Quality evidence: {report.overall_status}",
        f"Selection: {report.selection}",
        f"Evidence scope: {report.evidence_scope}",
    ]
    for result in report.results:
        lines.append(
            f"{result.status.upper()} {result.id}: {result.message} [scope: {result.evidence_scope}]"
        )
    lines.append(f"Human review boundary: {report.human_review_boundary}")
    return "\n".join(lines) + "\n"


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_markdown(report: Report) -> str:
    lines = [
        "# Quality evidence",
        "",
        f"Overall status: **{report.overall_status}**.",
        "",
        f"Evidence scope: {_markdown_cell(report.evidence_scope)}",
        "",
        "| Check | Status | Evidence scope | Result |",
        "|---|---|---|---|",
    ]
    for result in report.results:
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (result.id, result.status, result.evidence_scope, result.message)
            )
            + " |"
        )
    lines.extend(
        [
            "",
            f"Human review boundary: {_markdown_cell(report.human_review_boundary)}",
            "",
        ]
    )
    return "\n".join(lines)


def render_fatal(output_format: str, message: str, root: Path) -> str:
    safe = sanitize_message(message, root)
    if output_format == "json":
        return json.dumps(
            {
                "schema_version": REPORT_SCHEMA_VERSION,
                "overall_status": "error",
                "diagnostics": [{"id": "runner.config", "status": "error", "message": safe}],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
    if output_format == "markdown":
        return f"# Quality evidence\n\nOverall status: **error**.\n\n`runner.config`: {_markdown_cell(safe)}\n"
    return f"ERROR runner.config: {safe}\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--profile")
    selection.add_argument("--check", action="append", default=[])
    parser.add_argument("--changed-from")
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    return parser


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = repository_root()
    try:
        matrix = load_matrix(root / MATRIX_FILE, root)
        selection, selected, changed_from = resolve_selection(
            matrix, args.profile, args.check, args.changed_from
        )
        report = run_quality(root, matrix, selection, selected, changed_from)
        rendered = {
            "text": render_text,
            "json": render_json,
            "markdown": render_markdown,
        }[args.format](report)
        sys.stdout.write(rendered)
        return report.exit_code
    except (MatrixError, RunnerError) as exc:
        sys.stdout.write(render_fatal(args.format, str(exc), root))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
