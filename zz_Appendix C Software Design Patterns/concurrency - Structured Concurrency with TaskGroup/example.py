"""Read-only AST trace of Chapter 21's structured-concurrency owner."""

from __future__ import annotations

import ast
from pathlib import Path


OWNER_RELATIVE = Path("chapter-21-async/structured_async.py")


class SourceTraceError(Exception):
    """The owning source cannot provide the expected reading evidence."""


class OwnershipTrace:
    def __init__(
        self,
        taskgroup_scopes: tuple[str, ...],
        timeout_scopes: tuple[str, ...],
        create_task_calls: int,
        cleanup_functions: tuple[str, ...],
    ) -> None:
        self.taskgroup_scopes = taskgroup_scopes
        self.timeout_scopes = timeout_scopes
        self.create_task_calls = create_task_calls
        self.cleanup_functions = cleanup_functions


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def trace_owner(path: Path) -> OwnershipTrace:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise SourceTraceError("owner_source_unavailable") from error
    try:
        tree = ast.parse(source, filename=path.name)
    except SyntaxError as error:
        raise SourceTraceError("owner_source_invalid") from error

    taskgroup_scopes: list[str] = []
    timeout_scopes: list[str] = []
    cleanup_functions: list[str] = []
    create_task_calls = 0

    for function in (
        node for node in tree.body if isinstance(node, ast.AsyncFunctionDef)
    ):
        calls = [node for node in ast.walk(function) if isinstance(node, ast.Call)]
        call_names = [_call_name(call.func) for call in calls]
        if any(name.endswith("TaskGroup") for name in call_names):
            taskgroup_scopes.append(function.name)
        if any(name.endswith("timeout") for name in call_names):
            timeout_scopes.append(function.name)
        create_task_calls += sum(name.endswith("create_task") for name in call_names)
        if any(
            isinstance(node, ast.Try) and node.finalbody for node in ast.walk(function)
        ):
            cleanup_functions.append(function.name)

    if not taskgroup_scopes or not cleanup_functions:
        raise SourceTraceError("ownership_signals_missing")
    return OwnershipTrace(
        tuple(taskgroup_scopes),
        tuple(timeout_scopes),
        create_task_calls,
        tuple(cleanup_functions),
    )


def main() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    trace = trace_owner(repository_root / OWNER_RELATIVE)
    print(f"owner={OWNER_RELATIVE.as_posix()}")
    print(f"taskgroup_scopes={list(trace.taskgroup_scopes)}")
    print(f"timeout_scopes={list(trace.timeout_scopes)}")
    print(f"create_task_calls={trace.create_task_calls}")
    print(f"cleanup_functions={list(trace.cleanup_functions)}")
    print("evidence=source-trace; behavior remains owned by Chapter 21 tests")


if __name__ == "__main__":
    main()
