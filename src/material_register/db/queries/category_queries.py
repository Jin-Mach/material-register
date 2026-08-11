from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.domain.category_dataclass import Category


class CategoryQueries:
    @staticmethod
    def create_category(
        connection: QSqlDatabase, name: str, notes: str
    ) -> tuple[bool, str, int | None]:
        query = QSqlQuery(connection)
        query.prepare("INSERT INTO categories (name, notes) VALUES (?, ?)")
        query.addBindValue(name)
        query.addBindValue(notes)
        ok = query.exec()
        error = ""
        category_id = None
        if ok:
            category_id = query.lastInsertId()
        else:
            error = query.lastError().text()
        return ok, error, category_id

    @staticmethod
    def update_category(
        connection: QSqlDatabase, category_id: int, name: str, notes: str
    ) -> tuple[bool, str]:
        query = QSqlQuery(connection)
        query.prepare("UPDATE categories SET name=?, notes=? WHERE id=?")
        query.addBindValue(name)
        query.addBindValue(notes)
        query.addBindValue(category_id)
        ok = query.exec()
        error = ""
        if not ok:
            error = query.lastError().text()
        return ok, error

    @staticmethod
    def get_categories(connection: QSqlDatabase) -> list[Category]:
        query = QSqlQuery(connection)
        if not query.exec("SELECT id, name, notes FROM categories ORDER BY name"):
            return []
        results = []
        while query.next():
            results.append(
                Category(
                    id=query.value(0),
                    name=query.value(1),
                    notes=query.value(2),
                )
            )
        return results

    @staticmethod
    def category_exists(
        connection: QSqlDatabase, name: str, ignored_id: int | None = None
    ) -> bool:
        query = QSqlQuery(connection)
        sql = "SELECT 1 FROM categories WHERE name = ?"
        if ignored_id is not None:
            sql += " AND id != ?"
        query.prepare(sql)
        query.addBindValue(name)
        if ignored_id is not None:
            query.addBindValue(ignored_id)
        if not query.exec():
            return False
        return query.next()

    @staticmethod
    def get_category_by_id(
        connection: QSqlDatabase, category_id: int
    ) -> Category | None:
        query = QSqlQuery(connection)
        query.prepare("SELECT name, notes FROM categories WHERE id = ?")
        query.addBindValue(category_id)
        if not query.exec():
            return None
        if not query.next():
            return None
        return Category(id=category_id, name=query.value(0), notes=query.value(1))

    @staticmethod
    def get_total_count(connection: QSqlDatabase) -> int:
        query = QSqlQuery(connection)
        query.exec("SELECT COUNT(*) FROM categories")
        if query.next():
            return query.value(0)
        return 0
