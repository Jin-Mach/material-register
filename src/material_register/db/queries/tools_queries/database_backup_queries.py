from PySide6.QtSql import QSqlDatabase, QSqlQuery


class DatabaseBackupQueries:
    @staticmethod
    def has_data(connection: QSqlDatabase) -> bool:
        query = QSqlQuery(connection)
        if not query.exec("""
            SELECT
                EXISTS(SELECT 1 FROM customers LIMIT 1)
                OR EXISTS(SELECT 1 FROM categories LIMIT 1)
                OR EXISTS(SELECT 1 FROM commodities LIMIT 1)
                OR EXISTS(SELECT 1 FROM transactions LIMIT 1)
        """):
            return False
        if not query.next():
            return False
        result = query.value(0)
        return bool(result)
