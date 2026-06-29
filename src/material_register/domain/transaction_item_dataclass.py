from dataclasses import dataclass


@dataclass(frozen=True)
class TransactionItem:
    commodity_id: int | None = None
    unit_count: int | float | None = None
    price_per_unit: int | float | None = None