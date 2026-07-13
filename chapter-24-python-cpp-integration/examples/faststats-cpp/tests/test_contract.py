from __future__ import annotations

from fractions import Fraction
from decimal import Decimal
from math import isclose

import pytest

import faststats_cpp
from faststats_cpp import _reference


def fields(summary: object) -> tuple[object, ...]:
    return tuple(
        getattr(summary, name)
        for name in (
            "count",
            "minimum",
            "maximum",
            "mean",
            "anomaly_count",
            "anomaly_ratio",
        )
    )


@pytest.mark.parametrize(
    ("samples", "threshold"),
    [
        ([1], 0),
        ([1, 2.5, -3], 1.25),
        ([-3, -3, -1], 0.5),
        ([1e150, -1e150], 1e150),
    ],
)
def test_native_matches_reference(samples: list[int | float], threshold: int | float) -> None:
    expected = _reference.summarize(samples, threshold=threshold)
    actual = faststats_cpp.summarize(samples, threshold=threshold)
    assert actual.count == expected.count
    assert actual.anomaly_count == expected.anomaly_count
    for name in ("minimum", "maximum", "mean", "anomaly_ratio"):
        assert isclose(
            getattr(actual, name),
            getattr(expected, name),
            rel_tol=1e-12,
            abs_tol=1e-12,
        )


def test_final_mean_and_tolerance_band_are_explicit() -> None:
    summary = faststats_cpp.summarize([-3, -3, -1], threshold=0.5)
    assert summary.anomaly_count == 3
    equality = faststats_cpp.summarize([0.0, 2.0], threshold=1.0)
    assert equality.anomaly_count == 0


class FloatLike:
    def __float__(self) -> float:
        return 1.0


class IntSubclass(int):
    pass


@pytest.mark.parametrize(
    "value",
    [True, Fraction(1, 2), Decimal("1.0"), FloatLike(), IntSubclass(1), "1"],
)
def test_iterable_rejects_non_exact_builtin_numbers(value: object) -> None:
    with pytest.raises(TypeError):
        faststats_cpp.summarize([value])
    with pytest.raises(TypeError):
        _reference.summarize([value])


@pytest.mark.parametrize(
    "samples",
    [[], [float("nan")], [float("inf")], [1e150 * 1.000000000000001], [2**53 + 1]],
)
def test_invalid_numeric_batches_raise_value_error(samples: list[int | float]) -> None:
    with pytest.raises(ValueError):
        faststats_cpp.summarize(samples)


@pytest.mark.parametrize("threshold", [-1, float("nan"), float("inf"), 1e151])
def test_invalid_threshold_raises_value_error(threshold: float) -> None:
    with pytest.raises(ValueError):
        faststats_cpp.summarize([1.0], threshold=threshold)


def test_boundary_sizes() -> None:
    assert faststats_cpp.summarize([1.0] * 1_000_000).count == 1_000_000
    with pytest.raises(ValueError):
        faststats_cpp.summarize(1.0 for _ in range(1_000_001))


def test_summary_is_read_only_and_repr_is_useful() -> None:
    summary = faststats_cpp.summarize([1.0, 2.0])
    assert "Summary(count=2" in repr(summary)
    with pytest.raises(AttributeError):
        summary.mean = 10.0


def test_custom_domain_error_is_translated() -> None:
    from faststats_cpp import _native

    with pytest.raises(faststats_cpp.FaststatsError, match="demonstration"):
        _native._raise_domain_error_for_test()
