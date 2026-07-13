"""Educational benchmark: correctness first, then median timings."""

from __future__ import annotations

import argparse
import platform
import statistics
import sys
import time

from faststats_rs import summarize as native_summarize
from faststats_rs._reference import summarize as reference_summarize


def elapsed(function: object, values: list[float], repeats: int) -> float:
    samples: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        function(values, threshold=25.0)  # type: ignore[operator]
        samples.append(time.perf_counter() - started)
    return statistics.median(samples)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    arguments = parser.parse_args()
    sizes = [10, 10_000] if arguments.smoke else [10, 1_000, 100_000]
    repeats = 3 if arguments.smoke else 7
    print(f"Python {platform.python_version()} on {platform.system()} {platform.machine()}")
    print("profile=release; sequence extraction/copy is included")
    for size in sizes:
        values = [float(index % 101) for index in range(size)]
        expected = reference_summarize(values, threshold=25.0)
        actual = native_summarize(values, threshold=25.0)
        if actual.count != expected.count or abs(actual.mean - expected.mean) > 1e-12:
            raise RuntimeError("benchmark implementations disagree")
        native_summarize(values, threshold=25.0)
        reference_summarize(values, threshold=25.0)
        python_time = elapsed(reference_summarize, values, repeats)
        rust_time = elapsed(native_summarize, values, repeats)
        print(f"n={size}: python={python_time:.6f}s rust={rust_time:.6f}s")
    print("Interpret measurements; no minimum speedup is promised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
