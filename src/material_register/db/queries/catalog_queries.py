from PySide6.QtSql import QSqlQuery, QSqlDatabase


class CatalogQueries:

    @staticmethod
    def create_category(connection: QSqlDatabase, category_name: str) -> bool:
        query = QSqlQuery(connection)
        query.prepare(f"INSERT INTO categories (name) VALUES (?)")
        query.addBindValue(category_name)
        return query.exec()

    @staticmethod
    def update_category(connection: QSqlDatabase, category_id: int, category_name: str) -> bool:
        query = QSqlQuery(connection)
        query.prepare(f"UPDATE categories SET name=? WHERE id=?")
        query.addBindValue(category_name)
        query.addBindValue(category_id)
        return query.exec()

    @staticmethod
    def get_categories(connection: QSqlDatabase) -> list[dict[str, int | str]]:
        query = QSqlQuery(connection)
        if not query.exec("SELECT id, name FROM categories ORDER BY name"):
            return []
        results = []
        while query.next():
            results.append({"id": query.value(0), "name": query.value(1)})
        return results