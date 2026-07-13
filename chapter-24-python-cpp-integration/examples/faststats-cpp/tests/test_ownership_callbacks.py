from __future__ import annotations

import pytest

import faststats_cpp


def test_reference_internal_and_keep_alive_relationships() -> None:
    dataset = faststats_cpp.Dataset("sensor-A")
    metadata = dataset.metadata
    view = faststats_cpp.BorrowingView(dataset)
    del dataset
    assert metadata.label == "sensor-A"
    assert view.label == "sensor-A"


def test_smart_holder_transfers_unique_ownership_once() -> None:
    before = faststats_cpp.TrackedResource.live_count()
    resource = faststats_cpp.make_resource("temporary")
    assert resource.name == "temporary"
    assert faststats_cpp.TrackedResource.live_count() == before + 1
    faststats_cpp.consume_resource(resource)
    assert faststats_cpp.TrackedResource.live_count() == before
    with pytest.raises(ValueError):
        _ = resource.name


def test_callback_happy_path_and_exception_propagation() -> None:
    events: list[tuple[int, float]] = []
    summary = faststats_cpp.summarize_with_progress(
        [1.0, 2.0, 3.0], threshold=1.0, callback=lambda count, mean: events.append((count, mean))
    )
    assert summary.count == 3
    assert events == [(3, 2.0)]

    def fail(_count: int, _mean: float) -> None:
        raise LookupError("callback stopped")

    with pytest.raises(LookupError, match="callback stopped"):
        faststats_cpp.summarize_with_progress([1.0], callback=fail)


def test_trampoline_is_retained_by_native_runner() -> None:
    events: list[int] = []

    class Recorder(faststats_cpp.ProgressObserver):
        def on_progress(self, completed: int) -> None:
            events.append(completed)

    observer = Recorder()
    runner = faststats_cpp.ObserverRunner(observer)
    del observer
    runner.run(7)
    assert events == [7]

    class Failing(faststats_cpp.ProgressObserver):
        def on_progress(self, completed: int) -> None:
            raise RuntimeError(f"failed at {completed}")

    with pytest.raises(RuntimeError, match="failed at 8"):
        faststats_cpp.ObserverRunner(Failing()).run(8)
