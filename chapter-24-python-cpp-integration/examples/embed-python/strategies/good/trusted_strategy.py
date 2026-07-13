"""Trusted local strategy used by the embedding acceptance test."""

from __future__ import annotations


def evaluate(values: list[float]) -> float:
    return float(sum(values))
