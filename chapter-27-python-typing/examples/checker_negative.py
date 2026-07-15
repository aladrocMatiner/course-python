"""Deliberately invalid consumer; the verifier expects three error categories."""

from typed_inventory import Inventory, InventoryRow, PriceSource


bad_row: InventoryRow = {"sku": "PART-7", "quantity": "many"}
Inventory().add("not an inventory row")


class BrokenPrices:
    def unit_price(self, sku: int) -> str:
        return str(sku)


prices: PriceSource = BrokenPrices()

