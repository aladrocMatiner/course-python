"""Readable oracle for the native contract; never an automatic fallback."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite
import collections.abc as _abc
from typing import cast

MAX_SAMPLES = 1_000_000
MAX_EXACT_INTEGER = 2**53
MAX_MAGNITUDE = 1e150
TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class Summary:
    count: int
    minimum: float
    maximum: float
    mean: float
    anomaly_count: int
    anomaly_ratio: float


def _value(raw: object) -> float:
    if type(raw) not in (int, float):
        raise TypeError("samples must be built-in int or float values (not bool or subclasses)")
    numeric = cast(int | float, raw)
    if type(raw) is int and abs(numeric) > MAX_EXACT_INTEGER:
        raise ValueError("integer samples require abs(value) <= 2**53")
    converted = float(numeric)
    if not isfinite(converted) or abs(converted) > MAX_MAGNITUDE:
        raise ValueError("samples must be finite and abs(value) <= 1e150")
    return converted


def _threshold(raw: object) -> float:
    if type(raw) not in (int, float):
        raise TypeError("threshold must be a built-in int or float")
    try:
        converted = float(cast(int | float, raw))
    except OverflowError as error:
        raise ValueError("threshold is outside the supported range") from error
    if not isfinite(converted) or not 0.0 <= converted <= MAX_MAGNITUDE:
        raise ValueError("threshold must be finite and in [0, 1e150]")
    return converted


def _copy_samples(samples: _abc.Iterable[object], *, allow_empty: bool = False) -> list[float]:
    copied: list[float] = []
    for sample in samples:
        if len(copied) == MAX_SAMPLES:
            raise ValueError("sample count must not exceed 1000000")
        copied.append(_value(sample))
    if not allow_empty and not copied:
        raise ValueError("sample count must be between 1 and 1000000")
    return copied


def summarize(samples: _abc.Iterable[object], *, threshold: object = 0.0) -> Summary:
    copied = _copy_samples(samples)
    checked_threshold = _threshold(threshold)
    mean = 0.0
    for count, sample in enumerate(copied, start=1):
        mean += (sample - mean) / count
    anomaly_count = sum(
        1
        for sample in copied
        if (delta := abs(sample - mean)) > checked_threshold
        and not isclose(delta, checked_threshold, rel_tol=TOLERANCE, abs_tol=TOLERANCE)
    )
    return Summary(
        count=len(copied),
        minimum=min(copied),
        maximum=max(copied),
        mean=mean,
        anomaly_count=anomaly_count,
        anomaly_ratio=anomaly_count / len(copied),
    )


class OnlineStats:
    """Transactional incremental reference implementation."""

    def __init__(self) -> None:
        self._count: int
        self._minimum: float
        self._maximum: float
        self._mean: float
        self.reset()

    def add(self, value: object) -> None:
        checked = _value(value)
        if self._count >= MAX_SAMPLES:
            raise ValueError("online sample count cannot exceed 1000000")
        if self._count == 0:
            self._minimum = self._maximum = self._mean = checked
            self._count = 1
            return
        self._minimum = min(self._minimum, checked)
        self._maximum = max(self._maximum, checked)
        self._count += 1
        self._mean += (checked - self._mean) / self._count

    def extend(self, values: _abc.Iterable[object]) -> None:
        copied = _copy_samples(values, allow_empty=True)
        if len(copied) > MAX_SAMPLES - self._count:
            raise ValueError("online sample count cannot exceed 1000000")
        old = (self._count, self._minimum, self._maximum, self._mean)
        try:
            for value in copied:
                self.add(value)
        except Exception:
            self._count, self._minimum, self._maximum, self._mean = old
            raise

    def reset(self) -> None:
        self._count = 0
        self._minimum = 0.0
        self._maximum = 0.0
        self._mean = 0.0

    @property
    def count(self) -> int:
        return self._count

    @property
    def minimum(self) -> float | None:
        return None if self._count == 0 else self._minimum

    @property
    def maximum(self) -> float | None:
        return None if self._count == 0 else self._maximum

    @property
    def mean(self) -> float | None:
        return None if self._count == 0 else self._mean
