from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class AdvancedSearchDataclass:
    clause: Literal["WHERE", "HAVING"]
    column_name: str
    query: str
    value: str | int | float | tuple[str, str]
