from .domain import Order


def main() -> int:
    order = Order(identifier=1, total=90.0)
    print(f"Order {order.identifier}: {order.total:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
