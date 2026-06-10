from dataclasses import dataclass

@dataclass(frozen=True)
class Commodity:
    name: str
    id: int | None = None
    category_id: int | None = None
    unit: str = "kg"
    default_price: float = 0.0
    notes: str | None = None
    active: int = 1