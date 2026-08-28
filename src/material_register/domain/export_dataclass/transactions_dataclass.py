from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransactionsExportDay:
    transaction_date: str | None = None
    transactions_list: list[TransactionsExportTransaction] | None = None


@dataclass(frozen=True)
class TransactionsExportTransaction:
    created_at: str | None = None
    payment_type: str | None = None
    customer_name: str | None = None
    document_number: str | None = None
    address: str | None = None
    transaction_items: list[TransactionExportItem] | None = None


@dataclass(frozen=True)
class TransactionExportItem:
    category: str | None = None
    commodity_name: str | None = None
    commodity_unit: str | None = None
    unit_count: float | None = None
    price_per_unit: float | None = None
