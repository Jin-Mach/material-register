from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.queries_constants import EXPORT_QUERY_IN, EXPORT_QUERY_OUT
from material_register.domain.export_dataclass import ExportItemIn, ExportItemOut


class ExportQueries:

    @staticmethod
    def load_export_data_in(db_connection: QSqlDatabase, from_date: str, to_date: str) -> tuple[bool, str, list[ExportItemIn]]:
        query = QSqlQuery(db_connection)
        query.prepare(EXPORT_QUERY_IN)
        query.addBindValue(from_date)
        query.addBindValue(to_date)
        ok = query.exec()
        if not ok:
            return False, query.lastError().text(), []
        results = []
        while query.next():
            results.append(ExportItemIn(
                category_name=query.value(0),
                commodity_name=query.value(1),
                commodity_unit=query.value(2),
                price_per_unit=query.value(3),
                total_quantity=query.value(4),
                total_price=query.value(5)
            ))
        return True, "", results

    @staticmethod
    def load_export_data_out(db_connection: QSqlDatabase, from_date: str, to_date: str) -> tuple[bool, str, list[ExportItemOut]]:
        query = QSqlQuery(db_connection)
        query.prepare(EXPORT_QUERY_OUT)
        query.addBindValue(from_date)
        query.addBindValue(to_date)
        ok = query.exec()
        if not ok:
            return False, query.lastError().text(), []
        results = []
        while query.next():
            results.append(ExportItemOut(
                category_name=query.value(0),
                commodity_name=query.value(1),
                commodity_unit=query.value(2),
                total_quantity=query.value(3)
            ))
        return True, "", results