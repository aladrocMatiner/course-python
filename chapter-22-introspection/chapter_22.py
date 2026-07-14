"""Importable introspection helpers used by Chapter 22 tests."""

import inspect
from collections.abc import Iterable
from typing import Any


def describe(value: object) -> dict[str, Any]:
    info: dict[str, Any] = {
        "type": type(value).__name__,
        "repr": repr(value),
        "is_callable": callable(value),
    }
    try:
        info["len"] = len(value)  # type: ignore[arg-type]
        info["has_len"] = True
    except TypeError:
        info["len"] = None
        info["has_len"] = False
    info["name_attr"] = getattr(value, "name", None)
    return info


def describe2(value: object) -> dict[str, Any]:
    info = describe(value)
    try:
        info["first_item"] = value[0]  # type: ignore[index]
        info["has_items"] = True
    except (TypeError, IndexError, KeyError):
        info["first_item"] = None
        info["has_items"] = False
    return info


def report_types(values: Iterable[object]) -> list[str]:
    return [f"{value!r} -> {type(value).__name__}" for value in values]


def call_method(obj: object, method_name: str, *args: object, **kwargs: object) -> Any:
    attribute = getattr(obj, method_name, None)
    if not callable(attribute):
        raise TypeError(f"{type(obj).__name__} has no callable '{method_name}'")
    return attribute(*args, **kwargs)


def require_named_params(fn: object, required_names: Iterable[str]) -> None:
    signature = inspect.signature(fn)
    names = tuple(required_names)
    probe = {name: object() for name in names}
    try:
        signature.bind(**probe)
    except TypeError as exc:
        name = getattr(fn, "__name__", type(fn).__name__)
        raise TypeError(
            f"{name} must accept these named arguments: {', '.join(names)}"
        ) from exc
