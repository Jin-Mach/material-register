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