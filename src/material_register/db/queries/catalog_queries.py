from PySide6.QtSql import QSqlQuery, QSqlDatabase


class CatalogQueries:

    @staticmethod
    def create_category(connection: QSqlDatabase, name: str, notes: str):
        query = QSqlQuery(connection)
        query.prepare("INSERT INTO categories (name, notes) VALUES (?, ?)")
        query.addBindValue(name)
        query.addBindValue(notes)
        ok = query.exec()
        error = ""
        if not ok:
            error = query.lastError().text()
        return ok, error

    @staticmethod
    def update_category(connection: QSqlDatabase, category_id: int, category_name: str) -> bool:
        query = QSqlQuery(connection)
        query.prepare("UPDATE categories SET name=? WHERE id=?")
        query.addBindValue(category_name)
        query.addBindValue(category_id)
        return query.exec()

    @staticmethod
    def get_categories(connection: QSqlDatabase) -> list[dict[str, int | str]]:
        query = QSqlQuery(connection)
        if not query.exec("SELECT id, name notes FROM categories ORDER BY name"):
            return []
        results = []
        while query.next():
            results.append({"id": query.value(0), "name": query.value(1)})
        return results

    @staticmethod
    def category_exists(connection: QSqlDatabase, name: str, ignored_id: int | None = None) -> bool:
        query = QSqlQuery(connection)
        sql = "SELECT 1 FROM categories WHERE name = ?"
        if ignored_id is not None:
            sql += " AND id != ?"
        query.prepare(sql)
        query.addBindValue(name)
        if ignored_id is not None:
            query.addBindValue(ignored_id)
        query.exec()
        return query.next()