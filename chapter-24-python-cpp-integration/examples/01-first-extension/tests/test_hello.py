from __future__ import annotations

import pytest

import hello_cpp


def test_add_happy_path_and_edge_case() -> None:
    assert hello_cpp.add(20, 22) == 42
    assert hello_cpp.add(-1, 1) == 0


def test_add_rejects_text() -> None:
    with pytest.raises(TypeError):
        hello_cpp.add("20", 22)
