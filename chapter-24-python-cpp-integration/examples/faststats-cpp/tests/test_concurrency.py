from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

import faststats_cpp

test_native = pytest.importorskip(
    "_faststats_test", reason="test-only CMake target is not shipped in wheels"
)


def test_two_calls_enter_released_native_region_together() -> None:
    values = [float(index % 17) for index in range(20_000)]
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(test_native.summarize_after_rendezvous, values, 2.0, 3000)
            for _ in range(2)
        ]
        results = [future.result(timeout=5) for future in futures]
    expected = faststats_cpp.summarize(values, threshold=2.0)
    assert [result.count for result in results] == [expected.count, expected.count]
    assert [result.anomaly_count for result in results] == [
        expected.anomaly_count,
        expected.anomaly_count,
    ]
