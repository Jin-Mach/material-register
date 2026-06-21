from src.material_register.domain.transaction_item_dataclass import TransactionItem

from PySide6.QtSql import QSqlDatabase, QSqlQuery


class TransactionItemsQueries:

    @staticmethod
    def insert_into_transaction_items(db_connection: QSqlDatabase, transaction_id: int, commodity_id: int,
                                      unit_count: int | float, price_per_unit: int | float) -> tuple[bool, str]:
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
    def get_transaction_items(db_connection: QSqlDatabase, transaction_id: int) -> list[TransactionItem]:
        query = QSqlQuery(db_connection)
        query.prepare("""
            SELECT commodity_id, unit_count, price_per_unit from transaction_items 
            WHERE transaction_id = ?
        """)
        query.addBindValue(transaction_id)
        if not query.exec():
            return []
        result = []
        while query.next():
            result.append(
                TransactionItem(
                    commodityId=query.value(0),
                    unitCount=query.value(1),
                    pricePerUnit=query.value(2)
                ))
        return result