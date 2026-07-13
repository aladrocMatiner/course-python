"""Pure Python correctness oracle; never an automatic native fallback."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite
from typing import Iterable

MAX_SAMPLES = 1_000_000
MAX_EXACT_INTEGER = 2**53
MAX_ABS_VALUE = 1e150


@dataclass(frozen=True, slots=True)
class ReferenceSummary:
    count: int
    minimum: float
    maximum: float
    mean: float
    anomaly_count: int
    anomaly_ratio: float


def _number(value: object, label: str) -> float:
    if type(value) is int:
        if abs(value) > MAX_EXACT_INTEGER:
            raise ValueError(f"{label} integer magnitude must not exceed 2**53")
        result = float(value)
    elif type(value) is float:
        result = value
    else:
        raise TypeError(f"{label} must be an exact built-in int or float")
    if not isfinite(result):
        raise ValueError("sample values must be finite")
    if abs(result) > MAX_ABS_VALUE:
        raise ValueError("sample values must have absolute value at most 1e150")
    return result


def summarize(
    samples: Iterable[int | float], *, threshold: int | float
) -> ReferenceSummary:
    values: list[float] = []
    for index, item in enumerate(samples):
        if index >= MAX_SAMPLES:
            raise ValueError("sample count must not exceed 1,000,000")
        values.append(_number(item, f"samples[{index}]"))
    if not values:
        raise ValueError("samples must contain at least one value")
    threshold_value = _number(threshold, "threshold")
    if threshold_value < 0:
        raise ValueError("threshold must be finite and between 0 and 1e150")

    mean = 0.0
    for count, value in enumerate(values, start=1):
        mean += (value - mean) / count
    anomaly_count = sum(
        1
        for value in values
        if abs(value - mean) > threshold_value
        and not isclose(
            abs(value - mean), threshold_value, rel_tol=1e-12, abs_tol=1e-12
        )
    )
    return ReferenceSummary(
        count=len(values),
        minimum=min(values),
        maximum=max(values),
        mean=mean,
        anomaly_count=anomaly_count,
        anomaly_ratio=anomaly_count / len(values),
    )
