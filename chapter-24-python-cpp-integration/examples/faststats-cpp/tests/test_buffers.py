from __future__ import annotations

from array import array
from ctypes import alignment, c_double, sizeof
from math import isclose

import pytest

import faststats_cpp


def test_read_buffer_matches_iterable_without_mutation() -> None:
    values = array("d", [1.0, 2.0, 5.0])
    before = values.tolist()
    buffered = faststats_cpp.summarize_buffer(values, threshold=1.0)
    copied = faststats_cpp.summarize(values, threshold=1.0)
    assert values.tolist() == before
    assert buffered.count == copied.count
    assert isclose(buffered.mean, copied.mean, rel_tol=1e-12, abs_tol=1e-12)


def test_normalize_happy_constant_and_boundary_values() -> None:
    values = array("d", [2.0, 4.0, 6.0])
    faststats_cpp.normalize_in_place(values)
    assert values.tolist() == [0.0, 0.5, 1.0]

    constant = array("d", [4.0, 4.0])
    faststats_cpp.normalize_in_place(constant)
    assert constant.tolist() == [0.0, 0.0]

    bounds = array("d", [-1e150, 1e150])
    faststats_cpp.normalize_in_place(bounds)
    assert bounds.tolist() == [0.0, 1.0]


def test_failed_numeric_validation_is_transactional() -> None:
    values = array("d", [1.0, float("nan"), 3.0])
    with pytest.raises(ValueError):
        faststats_cpp.normalize_in_place(values)
    assert values[0] == 1.0 and values[2] == 3.0
    assert values[1] != values[1]


def test_layout_and_mutability_are_checked_before_use() -> None:
    values = array("d", [1.0, 2.0, 3.0, 4.0])
    with pytest.raises(ValueError, match="contiguous"):
        faststats_cpp.summarize_buffer(memoryview(values)[::2])
    with pytest.raises(ValueError, match="writable"):
        faststats_cpp.normalize_in_place(memoryview(values).toreadonly())
    with pytest.raises(ValueError, match="one-dimensional"):
        faststats_cpp.summarize_buffer(memoryview(values).cast("B").cast("d", (2, 2)))
    with pytest.raises(ValueError, match="format"):
        faststats_cpp.summarize_buffer(array("i", [1, 2]))
    with pytest.raises(ValueError, match="length"):
        faststats_cpp.summarize_buffer(array("d"))


def test_misaligned_double_buffer_is_rejected_before_use() -> None:
    double_alignment = alignment(c_double)
    if double_alignment == 1:
        pytest.skip("this platform has no misaligned address for a native double")

    double_size = sizeof(c_double)
    storage = array("B", bytes(2 * double_size + double_alignment))
    base_address = storage.buffer_info()[0]
    offset = next(
        candidate
        for candidate in range(double_alignment)
        if (base_address + candidate) % double_alignment != 0
    )
    misaligned = memoryview(storage)[offset : offset + 2 * double_size].cast("d")
    before = storage.tobytes()

    with pytest.raises(ValueError, match="not aligned"):
        faststats_cpp.summarize_buffer(misaligned)
    with pytest.raises(ValueError, match="not aligned"):
        faststats_cpp.normalize_in_place(misaligned)

    assert storage.tobytes() == before


def test_buffer_size_limits() -> None:
    accepted = array("d", [1.0]) * 1_000_000
    assert faststats_cpp.summarize_buffer(accepted).count == 1_000_000
    rejected = accepted + array("d", [1.0])
    with pytest.raises(ValueError, match="length"):
        faststats_cpp.summarize_buffer(rejected)
