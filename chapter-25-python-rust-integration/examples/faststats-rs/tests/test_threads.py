from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, wait

import pytest

import faststats_rs


def test_two_threads_complete_detached_batch_work() -> None:
    values = [float(index % 101) for index in range(200_000)]
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(faststats_rs.summarize, values, threshold=20.0)
            for _ in range(2)
        ]
        done, pending = wait(futures, timeout=10)
    assert not pending
    assert [future.result().count for future in done] == [200_000, 200_000]


def test_distribution_does_not_expose_rendezvous() -> None:
    from faststats_rs import _native

    required = os.environ.get("FASTSTATS_REQUIRE_TEST_HOOKS") == "1"
    if required:
        assert hasattr(_native, "summarize_with_rendezvous")
    else:
        assert not hasattr(_native, "summarize_with_rendezvous")


def test_rendezvous_proves_concurrent_detached_entry() -> None:
    from faststats_rs import _native

    if not hasattr(_native, "summarize_with_rendezvous"):
        pytest.skip("test-hooks wheel is verified in the dedicated acceptance stage")
    values = [1.0, 2.0, 3.0]
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(_native.summarize_with_rendezvous, values, threshold=1.0)
            for _ in range(2)
        ]
        done, pending = wait(futures, timeout=8)
    assert not pending
    assert [future.result().count for future in done] == [3, 3]


def test_rendezvous_timeout_preserves_concurrency_failure() -> None:
    from faststats_rs import _native

    if not hasattr(_native, "summarize_with_rendezvous"):
        pytest.skip("test-hooks wheel is verified in the dedicated acceptance stage")
    with pytest.raises(RuntimeError, match="two detached calls did not enter concurrently"):
        _native.summarize_with_rendezvous([1.0], threshold=1.0)
