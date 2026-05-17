from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.domain.commodities_dataclass import Commodity


class CommoditiesQueries:

    @staticmethod
    def create_commodity(connection: QSqlDatabase, name: str, category_id: int, unit: str, default_price: float,
                         notes: str, active: int) -> tuple[bool, str]:
        query = QSqlQuery(connection)
        query.prepare("""
            INSERT INTO commodities (
                name, category_id, unit, default_price, notes, active
            ) VALUES (?, ?, ?, ?, ?, ?)
            """)
        query.addBindValue(name)
        query.addBindValue(category_id)
        query.addBindValue(unit)
        query.addBindValue(default_price)
        query.addBindValue(notes)
        query.addBindValue(active)
        error = ""
        ok = query.exec()
        if not ok:
            error = query.lastError().text()
        return ok, error

    @staticmethod
    def update_commodity(connection: QSqlDatabase, commodity_id: int, name: str, category_id: int, unit: str,
                         default_price: float, notes: str, active: int) -> tuple[bool, str]:
        query = QSqlQuery(connection)
        query.prepare("""
            UPDATE commodities SET
                name=?,
                category_id=?,
                unit=?,
                default_price=?,
                notes=?,
                active=?
            WHERE id=?
            """)
        query.addBindValue(name)
        query.addBindValue(category_id)
        query.addBindValue(unit)
        query.addBindValue(default_price)
        query.addBindValue(notes)
        query.addBindValue(active)
        query.addBindValue(commodity_id)
        error = ""
        ok = query.exec()
        if not ok:
            error = query.lastError().text()
        return ok, error

    @staticmethod
    def change_active(connection: QSqlDatabase, commodity_id: int, active: int) -> tuple[bool, str]:
        query = QSqlQuery(connection)
        query.prepare("UPDATE commodities SET active=? WHERE id=?")
        query.addBindValue(active)
        query.addBindValue(commodity_id)
        error = ""
        ok = query.exec()
        if not ok:
            error = query.lastError().text()
        return ok, error

    @staticmethod
    def get_commodities(connection: QSqlDatabase) -> list[Commodity]:
        query = QSqlQuery(connection)
        if not query.exec("""
            SELECT 
                id, name, category_id, unit, default_price, notes, active
            FROM commodities ORDER BY name
            """):
            return []
        results = []
        while query.next():
            results.append(
                Commodity(
                    id=query.value(0),
                    name=query.value(1),
                    category_id=query.value(2),
                    unit=query.value(3),
                    default_price=query.value(4),
                    notes=query.value(5),
                    active=query.value(6)
                ))
        return results