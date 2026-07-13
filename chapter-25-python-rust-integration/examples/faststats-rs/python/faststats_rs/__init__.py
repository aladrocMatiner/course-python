"""Public typed facade for the chapter 25 Rust extension."""

try:
    from ._native import OnlineStats, Summary, describe_payload, summarize
except ModuleNotFoundError as error:
    if error.name == "faststats_rs._native":
        raise ImportError(
            "faststats_rs native extension is not built; install a compatible wheel "
            "or run maturin develop inside an active virtual environment"
        ) from error
    raise

__all__ = ["OnlineStats", "Summary", "describe_payload", "summarize"]
