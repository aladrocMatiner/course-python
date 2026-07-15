"""Corrected counterpart to ``checker_negative.py``."""

from typing import assert_type

from typed_inventory import Inventory, InventoryRow, PriceSource


row: InventoryRow = {"sku": "PART-7", "quantity": 3}
inventory = Inventory().add(row)
assert_type(inventory, Inventory)


class FixedPrices:
    def unit_price(self, sku: str) -> float | None:
        return 1.25 if sku == "PART-7" else None


prices: PriceSource = FixedPrices()
assert_type(prices.unit_price("PART-7"), float | None)

