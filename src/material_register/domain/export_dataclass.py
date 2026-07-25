from dataclasses import dataclass

@dataclass(frozen=True)
class ExportItemIn:
    category_name: str | None = None
    commodity_name: str | None = None
    commodity_unit: str | None = None
    price_per_unit: float | None = None
    total_quantity: float | None = None
    total_price: float | None = None

@dataclass(frozen=True)
class ExportItemOut:
    category_name: str | None = None
    commodity_name: str | None = None
    commodity_unit: str | None = None
    total_quantity: float | None = None