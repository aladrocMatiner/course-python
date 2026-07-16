"""Read-only responsibility trace of Chapter 23's selector source owner."""

from __future__ import annotations

import ast
from pathlib import Path


OWNER_RELATIVE = Path(
    "chapter-23-network-programming/examples/telemetry/selector_hub.py"
)


class SourceTraceError(Exception):
    """The owning Chapter 23 source cannot be traced."""


class ReactorReadingTrace:
    def __init__(
        self,
        readiness_calls: tuple[str, ...],
        interest_calls: tuple[str, ...],
        dispatch_handlers: tuple[str, ...],
        cleanup_methods: tuple[str, ...],
        owner_names_reactor: bool,
    ) -> None:
        self.readiness_calls = readiness_calls
        self.interest_calls = interest_calls
        self.dispatch_handlers = dispatch_handlers
        self.cleanup_methods = cleanup_methods
        self.owner_names_reactor = owner_names_reactor


def trace_owner(path: Path) -> ReactorReadingTrace:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise SourceTraceError("owner_source_unavailable") from error
    try:
        tree = ast.parse(source, filename=path.name)
    except SyntaxError as error:
        raise SourceTraceError("owner_source_invalid") from error

    hub = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "SelectorTelemetryHub"
        ),
        None,
    )
    if hub is None:
        raise SourceTraceError("selector_owner_missing")

    method_names = {
        node.name
        for node in hub.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    attribute_calls = {
        node.func.attr
        for node in ast.walk(hub)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    readiness = tuple(name for name in ("select",) if name in attribute_calls)
    interests = tuple(
        name for name in ("register", "modify", "unregister") if name in attribute_calls
    )
    handlers = tuple(
        name for name in ("_accept", "_read", "_write") if name in method_names
    )
    cleanup = tuple(
        name
        for name in ("_expire_idle_peers", "_close_peer", "close")
        if name in method_names
    )
    if not readiness or len(handlers) != 3 or "close" not in cleanup:
        raise SourceTraceError("responsibility_signals_missing")

    owner_names_reactor = "reactor" in source.lower()
    return ReactorReadingTrace(
        readiness, interests, handlers, cleanup, owner_names_reactor
    )


def main() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    trace = trace_owner(repository_root / OWNER_RELATIVE)
    print(f"owner={OWNER_RELATIVE.as_posix()}")
    print(f"readiness_calls={list(trace.readiness_calls)}")
    print(f"interest_calls={list(trace.interest_calls)}")
    print(f"dispatch_handlers={list(trace.dispatch_handlers)}")
    print(f"cleanup_methods={list(trace.cleanup_methods)}")
    print(f"owner_names_reactor={'yes' if trace.owner_names_reactor else 'no'}")
    print(
        "interpretation=Reactor-like responsibility trace, not a nominal-pattern claim"
    )


if __name__ == "__main__":
    main()
