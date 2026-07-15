"""A consumer that must pass the pinned strict checker contract."""

from typing import assert_type

from typed_inventory import (
    Inventory,
    InventoryRow,
    PriceSource,
    first_matching,
    parse_row,
)


class Catalogue:
    def unit_price(self, sku: str) -> float | None:
        return {"PART-7": 2.5}.get(sku)


class LabelledInventory(Inventory):
    pass


row = parse_row({"sku": "part-7", "quantity": 2})
assert_type(row, InventoryRow)

match = first_matching([row], lambda item: item["quantity"] == 2)
assert_type(match, InventoryRow | None)

prices: PriceSource = Catalogue()
assert_type(prices.unit_price(row["sku"]), float | None)

inventory = LabelledInventory()
assert_type(inventory.add(row), LabelledInventory)

