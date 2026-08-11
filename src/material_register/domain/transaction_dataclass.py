from dataclasses import dataclass


@dataclass(frozen=True)
class Transaction:
    transaction_id: int | None = None
    transaction_type: str | None = None
    transaction_created_at: str | None = None
    payment_type: str | None = None
    customer_id: int | None = None
    customer_document_number: str | None = None
    customer_address: str | None = None
    customer_name: str | None = None
    transaction_notes: str | None = None
    total: float | None = None
    suffix: str | None = None
    company_normalized: str | None = None
    first_name_normalized: str | None = None
    last_name_normalized: str | None = None
    address_normalized: str | None = None
