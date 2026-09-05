from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryExportItemIn:
    category_name: str | None = None
    payment_type: str | None = None
    commodity_name: str | None = None
    commodity_unit: str | None = None
    price_per_unit: float | None = None
    total_quantity: float | None = None
    total_price: float | None = None


@dataclass(frozen=True)
class SummaryExportItemOut:
    category_name: str | None = None
    commodity_name: str | None = None
    commodity_unit: str | None = None
    total_quantity: float | None = None


@dataclass
class SummaryItemDataIn:
    payment_type: str | None = None
    commodity_name: str | None = None
    commodity_unit: str | None = None
    price_per_unit: float | None = None
    total_quantity: float | None = None
    total_price: float = 0.0


@dataclass(frozen=True)
class SummaryItemDataOut:
    commodity_name: str | None = None
    commodity_unit: str | None = None
    total_quantity: float = 0.0
