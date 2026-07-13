from __future__ import annotations

import pytest

from faststats_rs import OnlineStats, summarize


def snapshot(stats: OnlineStats) -> tuple[int, float | None, float | None, float | None]:
    return stats.count, stats.minimum, stats.maximum, stats.mean


def test_summary_is_frozen_and_readable() -> None:
    summary = summarize([1, 2, 3], threshold=1)
    assert summary.count == 3
    assert "Summary(count=3" in repr(summary)
    with pytest.raises(AttributeError):
        summary.mean = 99.0


def test_online_stats_lifecycle() -> None:
    stats = OnlineStats()
    assert snapshot(stats) == (0, None, None, None)
    stats.add(2)
    stats.extend([4.0, 6])
    assert snapshot(stats) == (3, 2.0, 6.0, 4.0)
    assert "OnlineStats(count=3" in repr(stats)
    stats.reset()
    assert snapshot(stats) == (0, None, None, None)


@pytest.mark.parametrize("bad", [True, "3", float("nan"), float("inf"), 1e151])
def test_online_stats_failure_is_transactional(bad: object) -> None:
    stats = OnlineStats()
    stats.extend([1, 2, 3])
    before = snapshot(stats)
    with pytest.raises((TypeError, ValueError)):
        stats.extend([4, bad, 5])
    assert snapshot(stats) == before


def test_online_stats_limit_is_transactional() -> None:
    stats = OnlineStats()
    stats.extend([0.0] * 1_000_000)
    before = snapshot(stats)
    with pytest.raises(ValueError, match="1,000,000"):
        stats.add(0)
    assert snapshot(stats) == before


def test_empty_extend_is_a_noop() -> None:
    stats = OnlineStats()
    stats.extend([])
    assert snapshot(stats) == (0, None, None, None)
