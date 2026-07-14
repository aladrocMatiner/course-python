import unittest

from mi_app.domain import Order


class DomainTests(unittest.TestCase):
    def test_order_keeps_identifier_and_total(self) -> None:
        order = Order(identifier=7, total=3.5)
        self.assertEqual(7, order.identifier)
        self.assertEqual(3.5, order.total)


if __name__ == "__main__":
    unittest.main()
