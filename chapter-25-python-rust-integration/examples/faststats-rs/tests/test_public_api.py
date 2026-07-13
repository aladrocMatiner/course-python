from __future__ import annotations

import faststats_rs


def test_public_api_is_explicit() -> None:
    assert faststats_rs.__all__ == [
        "OnlineStats",
        "Summary",
        "describe_payload",
        "summarize",
    ]


def test_public_objects_report_package_module() -> None:
    assert faststats_rs.Summary.__module__ == "faststats_rs._native"
    assert faststats_rs.OnlineStats.__module__ == "faststats_rs._native"
