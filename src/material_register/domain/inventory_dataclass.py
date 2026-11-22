from dataclasses import dataclass


@dataclass
class InventoryHistoryDataclass:
    history_data: list[list[str | float]] | None = None
    total: float | None = None
