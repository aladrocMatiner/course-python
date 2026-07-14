from dataclasses import dataclass


@dataclass
class Order:
    identifier: int
    total: float
