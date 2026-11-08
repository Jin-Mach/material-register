from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class AdvancedSearchDataclass:
    clause: Literal["WHERE", "HAVING"]
    column_name: str
    query: str
    value: str | int | float | tuple[str, str]


@dataclass()
class MaterialSearchDataclass:
    category_id: int | None = None
    commodity_id: int | None = None
    amount_operator: str | None = None
    amount_value: float | None = (None,)
    price_per_unit_operator: str | None = None
    price_per_unit_value: float | None = None
    total_price_operator: str | None = None
    total_price_value: float | None = None
