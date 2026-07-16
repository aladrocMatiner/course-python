"""Comparison-only trace of Chapter 21; it implements no Supervisor."""

from __future__ import annotations

import ast
from pathlib import Path


OWNER_RELATIVE = Path("chapter-21-async/structured_async.py")
RESTART_WORDS = ("restart", "supervisor", "backoff")


class SourceTraceError(Exception):
    """The Chapter 21 source cannot be compared safely."""


class ComparisonTrace:
    def __init__(
        self,
        taskgroup_scopes: tuple[str, ...],
        cleanup_functions: tuple[str, ...],
        restart_signals: tuple[str, ...],
    ) -> None:
        self.taskgroup_scopes = taskgroup_scopes
        self.cleanup_functions = cleanup_functions
        self.restart_signals = restart_signals


def trace_owner(path: Path) -> ComparisonTrace:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise SourceTraceError("owner_source_unavailable") from error
    try:
        tree = ast.parse(source, filename=path.name)
    except SyntaxError as error:
        raise SourceTraceError("owner_source_invalid") from error

    taskgroup_scopes: list[str] = []
    cleanup_functions: list[str] = []
    names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            names.add(node.attr.lower())

    for function in (
        node for node in tree.body if isinstance(node, ast.AsyncFunctionDef)
    ):
        if any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "TaskGroup"
            for node in ast.walk(function)
        ):
            taskgroup_scopes.append(function.name)
        if any(
            isinstance(node, ast.Try) and node.finalbody for node in ast.walk(function)
        ):
            cleanup_functions.append(function.name)

    restart_signals = tuple(
        word for word in RESTART_WORDS if any(word in name for name in names)
    )
    if not taskgroup_scopes:
        raise SourceTraceError("taskgroup_scope_missing")
    return ComparisonTrace(
        tuple(taskgroup_scopes), tuple(cleanup_functions), restart_signals
    )


def main() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    trace = trace_owner(repository_root / OWNER_RELATIVE)
    print(f"owner={OWNER_RELATIVE.as_posix()}")
    print(f"owned_scopes={list(trace.taskgroup_scopes)}")
    print(f"cleanup_functions={list(trace.cleanup_functions)}")
    print(f"restart_policy={'present' if trace.restart_signals else 'absent'}")
    print("comparison=TaskGroup ownership only; no Supervisor implementation claim")


if __name__ == "__main__":
    main()
