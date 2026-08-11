from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.queries_constants import (
    TRANSACTIONS_QUERY_IN,
    TRANSACTIONS_QUERY_OUT,
)
from material_register.domain.transaction_dataclass import Transaction


class TransactionsLoadQueries:

    @staticmethod
    def load_transaction_in(db_connection: QSqlDatabase) -> list[Transaction]:
        query = QSqlQuery(db_connection)
        if not query.exec(TRANSACTIONS_QUERY_IN):
            return []
        results = []
        while query.next():
            results.append(Transaction(
                transaction_id=query.value("transaction_id"),
                transaction_type=query.value("transaction_type"),
                transaction_created_at=query.value("transaction_created_at"),
                payment_type=query.value("transaction_payment_type"),
                customer_id=query.value("customer_id"),
                customer_document_number=query.value("customer_document_number"),
                customer_address=query.value("customer_address"),
                customer_name=query.value("customer_name"),
                transaction_notes=query.value("transaction_notes"),
                total=query.value("total"),
                suffix=None,
                company_normalized=query.value("company_normalized"),
                first_name_normalized=query.value("first_name_normalized"),
                last_name_normalized=query.value("last_name_normalized"),
                address_normalized=query.value("address_normalized")
            ))
        return results

    @staticmethod
    def load_transactions_out(db_connection: QSqlDatabase) -> list[Transaction]:
        query = QSqlQuery(db_connection)
        if not query.exec(TRANSACTIONS_QUERY_OUT):
            return []
        results = []
        while query.next():
            results.append(Transaction(
                transaction_id=query.value("transaction_id"),
                transaction_type=query.value("transaction_type"),
                transaction_created_at=query.value("transaction_created_at"),
                payment_type=query.value("transaction_payment_type"),
                customer_id=query.value("customer_id"),
                customer_document_number=query.value("customer_document_number"),
                customer_address=query.value("customer_address"),
                customer_name=query.value("customer_name"),
                transaction_notes=query.value("transaction_notes"),
                total=query.value("total"),
                suffix=query.value("suffix"),
                company_normalized=query.value("company_normalized"),
                first_name_normalized=query.value("first_name_normalized"),
                last_name_normalized=query.value("last_name_normalized"),
                address_normalized=query.value("address_normalized")
            ))
        return results