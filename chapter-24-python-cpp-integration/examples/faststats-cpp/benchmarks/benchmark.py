"""Educational benchmark: verify first, then report medians without a speedup gate."""

from __future__ import annotations

import argparse
import math
import platform
import statistics
import sys
import time
from collections.abc import Callable
from dataclasses import astuple

import faststats_cpp
from faststats_cpp import _reference


def median_seconds(function: Callable[[], object], *, repeats: int) -> float:
    function()  # warm-up
    samples: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        function()
        samples.append(time.perf_counter() - started)
    return statistics.median(samples)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--profile", choices=("debug", "release", "unknown"), default="unknown")
    args = parser.parse_args()
    if not 3 <= args.repeats <= 101:
        parser.error("--repeats must be between 3 and 101")

    print(f"Python={platform.python_version()} platform={platform.platform()} profile={args.profile}")
    print("size\tpython median (s)\tnative median (s)\tnative/python")
    for size in (1, 10, 1_000, 100_000):
        values = [float((index * 17) % 101) for index in range(size)]
        expected = _reference.summarize(values, threshold=10.0)
        actual = faststats_cpp.summarize(values, threshold=10.0)
        expected_fields = astuple(expected)
        actual_fields = tuple(
            getattr(actual, field)
            for field in (
                "count",
                "minimum",
                "maximum",
                "mean",
                "anomaly_count",
                "anomaly_ratio",
            )
        )
        integer_fields_match = (
            expected_fields[0] == actual_fields[0]
            and expected_fields[4] == actual_fields[4]
        )
        float_fields_match = all(
            math.isclose(
                float(expected_fields[index]),
                float(actual_fields[index]),
                rel_tol=1e-12,
                abs_tol=1e-12,
            )
            for index in (1, 2, 3, 5)
        )
        if not integer_fields_match or not float_fields_match:
            raise RuntimeError("reference/native parity failed before timing")
        python_time = median_seconds(
            lambda: _reference.summarize(values, threshold=10.0), repeats=args.repeats
        )
        native_time = median_seconds(
            lambda: faststats_cpp.summarize(values, threshold=10.0), repeats=args.repeats
        )
        ratio = native_time / python_time if python_time else float("nan")
        print(f"{size}\t{python_time:.9f}\t{native_time:.9f}\t{ratio:.3f}")

    print("Interpretation: small calls may lose to boundary/conversion overhead; no ratio is a pass/fail gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
