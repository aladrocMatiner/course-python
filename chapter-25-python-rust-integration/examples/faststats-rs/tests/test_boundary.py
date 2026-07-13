from __future__ import annotations

import pytest

from faststats_rs import describe_payload, summarize


def test_string_bytes_and_optional_mapping() -> None:
    assert describe_payload("mätning", b"abc", None) == ("mätning", 3, False)
    assert describe_payload("قياس", b"\x00\xff", "note") == ("قياس", 2, True)


@pytest.mark.parametrize(
    "args",
    [
        (b"not-text", b"abc", None),
        ("label", "not-bytes", None),
        ("label", b"abc", 42),
    ],
)
def test_invalid_boundary_type_is_a_python_error(args: tuple[object, object, object]) -> None:
    with pytest.raises(TypeError):
        describe_payload(*args)


def test_generator_is_copied_before_computation() -> None:
    values = (value for value in [1, 2, 3])
    assert summarize(values, threshold=1).count == 3
