from __future__ import annotations

import pytest

import first_pyo3_extension


def test_happy_path() -> None:
    assert first_pyo3_extension.double(21) == 42
    assert first_pyo3_extension.greeting("Ada") == "Hello, Ada, from Rust!"


def test_wrong_type_is_reported_by_python() -> None:
    with pytest.raises(TypeError):
        first_pyo3_extension.double("21")


def test_overflow_is_a_recoverable_value_error() -> None:
    with pytest.raises(ValueError, match="overflow"):
        first_pyo3_extension.double(2**62)
