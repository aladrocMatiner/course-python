"""Educational benchmark: correctness first, then median timings."""

from __future__ import annotations

import argparse
import math
import platform
import statistics
import sys
import time

from faststats_rs import summarize as native_summarize
from faststats_rs._reference import summarize as reference_summarize


def assert_equivalent(actual: object, expected: object) -> None:
    for field in ("count", "minimum", "maximum", "mean", "anomaly_count", "anomaly_ratio"):
        actual_value = getattr(actual, field)
        expected_value = getattr(expected, field)
        if isinstance(expected_value, float):
            if not math.isclose(actual_value, expected_value, rel_tol=1e-12, abs_tol=1e-12):
                raise RuntimeError(f"benchmark implementations disagree on {field}")
        elif actual_value != expected_value:
            raise RuntimeError(f"benchmark implementations disagree on {field}")


def capture_expected_error(
    function: object, values: list[object], threshold: object
) -> Exception:
    try:
        function(values, threshold=threshold)  # type: ignore[operator]
    except (TypeError, ValueError) as error:
        return error
    except Exception as error:
        raise RuntimeError(
            f"benchmark oracle probe raised unexpected {type(error).__name__}"
        ) from error
    raise RuntimeError("benchmark oracle probe unexpectedly succeeded")


def assert_error_contract() -> None:
    probes: list[tuple[list[object], object, type[Exception], str]] = [
        ([True], 25.0, TypeError, "exact built-in"),
        ([float("nan")], 25.0, ValueError, "finite"),
        ([1.0], -1.0, ValueError, "threshold"),
    ]
    for values, threshold, expected_type, message_marker in probes:
        reference_error = capture_expected_error(reference_summarize, values, threshold)
        native_error = capture_expected_error(native_summarize, values, threshold)
        if type(reference_error) is not expected_type or type(native_error) is not expected_type:
            raise RuntimeError(
                "benchmark implementations disagree on the public exception type"
            )
        if message_marker not in str(reference_error) or message_marker not in str(native_error):
            raise RuntimeError(
                "benchmark implementations disagree on the public error category"
            )


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
    print(
        f"warmup-runs=1; timed-repetitions={repeats}; statistic=median; "
        f"sizes={','.join(str(size) for size in sizes)}"
    )
    assert_error_contract()
    print("error-contract=TypeError/ValueError parity checked before timing")
    for size in sizes:
        values = [float(index % 101) for index in range(size)]
        expected = reference_summarize(values, threshold=25.0)
        actual = native_summarize(values, threshold=25.0)
        assert_equivalent(actual, expected)
        native_summarize(values, threshold=25.0)
        reference_summarize(values, threshold=25.0)
        python_time = elapsed(reference_summarize, values, repeats)
        rust_time = elapsed(native_summarize, values, repeats)
        print(f"n={size}: python={python_time:.6f}s rust={rust_time:.6f}s")
    print("Interpret measurements; no minimum speedup is promised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
