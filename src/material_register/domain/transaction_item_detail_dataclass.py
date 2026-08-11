from dataclasses import dataclass


@dataclass(frozen=True)
class TransactionItemDetail:
    commodity_id: int | None = None
    unit_count: int | float | None = None
    price_per_unit: int | float | None = None
    commodity_name: str | None = None
    commodity_suffix: str | None = None
    category_name: str | None = None