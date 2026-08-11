from dataclasses import dataclass


@dataclass
class Customer:
    document_number: str
    address: str
    id: int | None = None
    company: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    notes: str | None = None
    created_at: str | None = None
    active: int = 1
    company_normalized: str | None = None
    first_name_normalized: str | None = None
    last_name_normalized: str | None = None
    address_normalized: str | None = None
