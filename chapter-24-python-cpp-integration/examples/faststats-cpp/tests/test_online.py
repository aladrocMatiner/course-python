from __future__ import annotations

import pytest

import faststats_cpp


def state(stats: faststats_cpp.OnlineStats) -> tuple[object, ...]:
    return (stats.count, stats.minimum, stats.maximum, stats.mean)


def test_online_happy_path_empty_and_reset() -> None:
    stats = faststats_cpp.OnlineStats()
    assert state(stats) == (0, None, None, None)
    stats.add(1)
    stats.extend([2.0, 3])
    assert state(stats) == (3, 1.0, 3.0, 2.0)
    assert "count=3" in repr(stats)
    stats.reset()
    assert state(stats) == (0, None, None, None)


def test_online_invalid_extension_preserves_full_state() -> None:
    stats = faststats_cpp.OnlineStats()
    stats.extend([1.0, 2.0])
    before = state(stats)
    with pytest.raises(ValueError):
        stats.extend([3.0, float("inf")])
    assert state(stats) == before
    with pytest.raises(TypeError):
        stats.extend([3.0, True])
    assert state(stats) == before


def test_online_total_limit_is_transactional() -> None:
    stats = faststats_cpp.OnlineStats()
    stats.extend([1.0] * 1_000_000)
    before = state(stats)
    with pytest.raises(ValueError, match="1000000"):
        stats.add(1.0)
    assert state(stats) == before
