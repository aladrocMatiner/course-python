"""Public typed facade for the chapter 24 native extension."""

from __future__ import annotations

try:
    from ._native import (
        BorrowingView,
        Dataset,
        FaststatsError,
        Metadata,
        ObserverRunner,
        OnlineStats,
        ProcessingMode,
        ProgressObserver,
        Summary,
        TrackedResource,
        consume_resource,
        make_resource,
        normalize_in_place,
        summarize,
        summarize_buffer,
        summarize_many,
        summarize_with_progress,
    )
except ModuleNotFoundError as _load_error:
    if _load_error.name == f"{__name__}._native":
        raise ImportError(
            "faststats_cpp native extension is not built; install its wheel instead of importing the source tree"
        ) from _load_error
    raise ImportError(
        "faststats_cpp native extension was found but one of its binary dependencies is missing"
    ) from _load_error
except ImportError as _load_error:
    raise ImportError(
        "faststats_cpp native extension could not load; verify the wheel's Python, ABI, and platform tags"
    ) from _load_error

__all__ = [
    "BorrowingView",
    "Dataset",
    "FaststatsError",
    "Metadata",
    "ObserverRunner",
    "OnlineStats",
    "ProcessingMode",
    "ProgressObserver",
    "Summary",
    "TrackedResource",
    "consume_resource",
    "make_resource",
    "normalize_in_place",
    "summarize",
    "summarize_buffer",
    "summarize_many",
    "summarize_with_progress",
]
