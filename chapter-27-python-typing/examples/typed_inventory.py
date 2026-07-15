"""Small runtime contracts used by Chapter 27.

The annotations in this module describe the typed core.  ``parse_row`` is the
explicit runtime boundary: annotations alone do not validate incoming values.
Importing the module performs no work and writes no files.
"""

from collections.abc import Callable, Iterable, Mapping
from typing import Protocol, Self, TypeVar, TypedDict


class InventoryRow(TypedDict):
    """A normalized inventory record used inside the typed core."""

    sku: str
    quantity: int


class PriceSource(Protocol):
    """Anything with this method shape can supply an optional unit price."""

    def unit_price(self, sku: str) -> float | None:
        """Return the unit price, or ``None`` when the SKU is unknown."""


T = TypeVar("T")


def parse_row(raw: Mapping[str, object]) -> InventoryRow:
    """Validate and normalize one untrusted mapping without mutating it.

    ``sku`` must be a string whose stripped form contains 1 through 32
    characters.  ``quantity`` must be a built-in ``int`` (never ``bool``) in
    the inclusive range 0 through 1,000,000.
    """

    if "sku" not in raw:
        raise TypeError("missing required field: sku")
    if "quantity" not in raw:
        raise TypeError("missing required field: quantity")

    raw_sku = raw["sku"]
    raw_quantity = raw["quantity"]

    if not isinstance(raw_sku, str):
        raise TypeError("sku must be a string")
    if type(raw_quantity) is not int:
        raise TypeError("quantity must be a built-in int, not bool")

    sku = raw_sku.strip().upper()
    if not sku:
        raise ValueError("sku must not be empty")
    if len(sku) > 32:
        raise ValueError("sku must contain at most 32 characters")
    if not 0 <= raw_quantity <= 1_000_000:
        raise ValueError("quantity must be between 0 and 1000000")

    return InventoryRow(sku=sku, quantity=raw_quantity)


def first_matching(items: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
    """Return the first matching item, or ``None`` after finite exhaustion."""

    for item in items:
        if predicate(item):
            return item
    return None


class Inventory:
    """A tiny fluent inventory that owns normalized copies of its rows."""

    def __init__(self) -> None:
        self._rows: list[InventoryRow] = []

    def add(self, row: InventoryRow) -> Self:
        """Validate, copy, and append ``row``; return this exact instance."""

        normalized = parse_row(row)
        self._rows.append(normalized)
        return self

    @property
    def rows(self) -> tuple[InventoryRow, ...]:
        """Return copies so callers cannot mutate the stored dictionaries."""

        return tuple(
            InventoryRow(sku=row["sku"], quantity=row["quantity"])
            for row in self._rows
        )

