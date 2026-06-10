from dataclasses import dataclass


@dataclass(frozen=True)
class TransactionItem:
    commodityId: int | None = None
    unitCount: int | float | None = None
    pricePerUnit: int | float | None = None