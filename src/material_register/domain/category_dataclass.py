from dataclasses import dataclass


@dataclass
class Category:
    id: int | None = None
    name: str | None = None
    notes: str | None = None