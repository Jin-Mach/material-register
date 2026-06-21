from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.queries_constants import TRANSACTIONS_BASIC_FILTER_QUERY
from material_register.domain.transaction_dataclass import Transaction


class TransactionsQueries:

    @staticmethod
    def insert_into_transactions(db_connection: QSqlDatabase, transaction_type: str, customer_id: int,
                                payment_type: str | None, notes: str) -> tuple[bool, str, int | None]:
        query = QSqlQuery(db_connection)
        query.prepare("INSERT INTO transactions (type, customer_id, payment_type, notes) VALUES (?, ?, ?, ?)")
        query.addBindValue(transaction_type)
        query.addBindValue(customer_id)
        query.addBindValue(payment_type)
        query.addBindValue(notes)
        ok = query.exec()
        error = ""
        transaction_id = None
        if ok:
            transaction_id = query.lastInsertId()
        else:
            error = query.lastError().text()
        return ok, error, transaction_id

    @staticmethod
    def delete_transaction(db_connection: QSqlDatabase, transaction_id: int) -> tuple[bool, str]:
        query = QSqlQuery(db_connection)
        query.prepare("DELETE FROM transactions WHERE id = ?")
        query.addBindValue(transaction_id)
        error = ""
        ok = query.exec()
        if not ok:
            error = query.lastError().text()
        return ok, error

    @staticmethod
    def get_basic_filter_data(db_connection: QSqlDatabase, transaction_type: str, from_date: str, end_date: str):
        query = QSqlQuery(db_connection)
        query.prepare(TRANSACTIONS_BASIC_FILTER_QUERY)
        query.addBindValue(transaction_type)
        query.addBindValue(from_date)
        query.addBindValue(end_date)
        if not query.exec():
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
                total=query.value("total"),
                suffix=query.value("suffix"),
                company_normalized=query.value("company_normalized"),
                first_name_normalized=query.value("first_name_normalized"),
                last_name_normalized=query.value("last_name_normalized"),
                address_normalized=query.value("address_normalized"),
            ))
        return results