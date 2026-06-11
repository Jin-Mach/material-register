from PySide6.QtSql import QSqlDatabase, QSqlQuery


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