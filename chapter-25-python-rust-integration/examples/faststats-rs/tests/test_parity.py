from __future__ import annotations

from fractions import Fraction
from decimal import Decimal
from math import isclose

import pytest

import faststats_rs
from faststats_rs._reference import summarize as reference_summarize


def assert_equivalent(samples: list[int | float], threshold: int | float) -> None:
    expected = reference_summarize(samples, threshold=threshold)
    actual = faststats_rs.summarize(samples, threshold=threshold)
    assert actual.count == expected.count
    assert actual.minimum == pytest.approx(expected.minimum, rel=1e-12, abs=1e-12)
    assert actual.maximum == pytest.approx(expected.maximum, rel=1e-12, abs=1e-12)
    assert actual.mean == pytest.approx(expected.mean, rel=1e-12, abs=1e-12)
    assert actual.anomaly_count == expected.anomaly_count
    assert actual.anomaly_ratio == pytest.approx(
        expected.anomaly_ratio, rel=1e-12, abs=1e-12
    )


@pytest.mark.parametrize(
    ("samples", "threshold"),
    [
        ([4], 0),
        ([-3, -3, -1], 0.5),
        ([-10.0, 0.0, 10.0], 5.0),
        ([0.0, 2.0], 1.0 + 5e-13),
        ([float(2**53), -float(2**53)], 1e150),
    ],
)
def test_reference_and_native_are_equivalent(
    samples: list[int | float], threshold: int | float
) -> None:
    assert_equivalent(samples, threshold)


def test_final_mean_second_pass_vector() -> None:
    summary = faststats_rs.summarize([-3, -3, -1], threshold=0.5)
    assert isclose(summary.mean, -7 / 3, rel_tol=1e-12, abs_tol=1e-12)
    assert summary.anomaly_count == 3


@pytest.mark.parametrize(
    "value",
    [True, Fraction(1, 2), Decimal("1.5"), type("FloatLike", (), {"__float__": lambda self: 1.0})()],
)
def test_rejected_number_types(value: object) -> None:
    with pytest.raises(TypeError):
        faststats_rs.summarize([value], threshold=0.0)
    with pytest.raises(TypeError):
        reference_summarize([value], threshold=0.0)


def test_numeric_subclasses_are_rejected() -> None:
    class SpecialFloat(float):
        pass

    class SpecialInt(int):
        pass

    for value in (SpecialFloat(1.0), SpecialInt(1)):
        with pytest.raises(TypeError):
            faststats_rs.summarize([value], threshold=0)


@pytest.mark.parametrize(
    "samples",
    [[], [float("nan")], [float("inf")], [1e151], [2**53 + 1]],
)
def test_invalid_values_raise_value_error(samples: list[int | float]) -> None:
    with pytest.raises(ValueError):
        faststats_rs.summarize(samples, threshold=0)
    with pytest.raises(ValueError):
        reference_summarize(samples, threshold=0)


@pytest.mark.parametrize("threshold", [-1, float("nan"), float("inf"), 1e151])
def test_invalid_threshold_raises_value_error(threshold: int | float) -> None:
    with pytest.raises(ValueError):
        faststats_rs.summarize([1], threshold=threshold)
    with pytest.raises(ValueError):
        reference_summarize([1], threshold=threshold)


def test_maximum_size_and_over_limit() -> None:
    values = [0.0] * 1_000_000
    summary = faststats_rs.summarize(values, threshold=0)
    assert summary.count == 1_000_000
    with pytest.raises(ValueError, match="1,000,000"):
        faststats_rs.summarize((*values, 0.0), threshold=0)


def test_native_extension_is_not_reference_fallback() -> None:
    from faststats_rs import _native

    assert _native.__file__ is not None
    assert not _native.__file__.endswith(".py")
