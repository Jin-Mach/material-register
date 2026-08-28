from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.export_config.export_queries_constants import (
    TRANSACTIONS_QUERY_IN,
)
from material_register.domain.export_dataclass.transactions_dataclass import (
    TransactionExportItemIn,
    TransactionsExportDay,
    TransactionsExportTransaction,
)


class TransactionsExportQueries:
    @staticmethod
    def load_export_data_in(
        db_connection: QSqlDatabase, from_date: str, to_date: str, customer_id: int | None
    ) -> tuple[bool, str, list[TransactionsExportDay]]:
        query = QSqlQuery(db_connection)
        if not query.prepare(TRANSACTIONS_QUERY_IN):
            return False, query.lastError().text(), []
        query.addBindValue(from_date)
        query.addBindValue(to_date)
        query.addBindValue(customer_id)
        query.addBindValue(customer_id)
        if not query.exec():
            return False, query.lastError().text(), []
        transaction_date = None
        current_day = None
        current_transaction = None
        results = []
        while query.next():
            actual_date = query.value(0)
            created_at = query.value(1)
            if transaction_date != actual_date:
                transaction_date = actual_date
                current_day = TransactionsExportDay(
                    transaction_date=actual_date, transactions_list=[]
                )
                current_transaction = TransactionsExportQueries._create_transaction(
                    query
                )
                current_day.transactions_list.append(current_transaction)
                results.append(current_day)
                continue
            if current_transaction.created_at == created_at:
                transaction_item = TransactionsExportQueries._create_transaction_item(
                    query
                )
                current_transaction.transaction_items.append(transaction_item)
                continue
            current_transaction = TransactionsExportQueries._create_transaction(query)
            current_day.transactions_list.append(current_transaction)
        return True, "", results

    @staticmethod
    def _create_transaction(query: QSqlQuery) -> TransactionsExportTransaction:
        transaction = TransactionsExportTransaction(
            created_at=query.value(1),
            payment_type=query.value(2),
            customer_name=query.value(10),
            document_number=query.value(3),
            address=query.value(4),
            transaction_items=[],
        )
        transaction.transaction_items.append(
            TransactionsExportQueries._create_transaction_item(query)
        )
        return transaction

    @staticmethod
    def _create_transaction_item(query: QSqlQuery) -> TransactionExportItemIn:
        return TransactionExportItemIn(
            category=query.value(9),
            commodity_name=query.value(7),
            commodity_unit=query.value(8),
            unit_count=query.value(5),
            price_per_unit=query.value(6),
        )
