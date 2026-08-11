from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.queries_constants import SELECTED_TRANSACTION_DATA
from material_register.domain.transaction_item_detail_dataclass import (
    TransactionItemDetail,
)


class TransactionItemsQueries:

    @staticmethod
    def insert_into_transaction_items(db_connection: QSqlDatabase, transaction_id: int, commodity_id: int,
                                      unit_count: float, price_per_unit: float) -> tuple[bool, str]:
        query = QSqlQuery(db_connection)
        query.prepare("""
                INSERT INTO transaction_items (
                    transaction_id,
                    commodity_id,
                    unit_count,
                    price_per_unit
                ) VALUES (?, ?, ?, ?)
            """)
        query.addBindValue(transaction_id)
        query.addBindValue(commodity_id)
        query.addBindValue(unit_count)
        query.addBindValue(price_per_unit)
        ok = query.exec()
        error = ""
        if not ok:
            error = query.lastError().text()
        return ok, error

    @staticmethod
    def delete_transaction_items(db_connection: QSqlDatabase, transaction_id: int) -> tuple[bool, str]:
        query = QSqlQuery(db_connection)
        query.prepare("""
                DELETE FROM transaction_items WHERE transaction_id = ?
        """)
        query.addBindValue(transaction_id)
        ok = query.exec()
        error = ""
        if not ok:
            error = query.lastError().text()
        return ok, error

    @staticmethod
    def get_transaction_items(db_connection: QSqlDatabase, transaction_id: int) -> list[TransactionItemDetail]:
        query = QSqlQuery(db_connection)
        query.prepare(SELECTED_TRANSACTION_DATA)
        query.addBindValue(transaction_id)
        if not query.exec():
            return []
        result = []
        while query.next():
            result.append(
                TransactionItemDetail(
                    commodity_id=query.value(0),
                    unit_count=query.value(1),
                    price_per_unit=query.value(2),
                    commodity_name=query.value(3),
                    commodity_suffix=query.value(4),
                    category_name=query.value(5)
                )
            )
        return result