from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.export_config.export_queries_constants import (
    SUMMARY_QUERY_IN,
    SUMMARY_QUERY_OUT,
)
from material_register.domain.export_dataclass.summary_dataclass import (
    SummaryExportItemIn,
    SummaryExportItemOut,
)


class SummaryExportQueries:
    @staticmethod
    def load_export_data_in(
        db_connection: QSqlDatabase, from_date: str, to_date: str
    ) -> tuple[bool, str, list[SummaryExportItemIn]]:
        query = QSqlQuery(db_connection)
        if not query.prepare(SUMMARY_QUERY_IN):
            return False, query.lastError().text(), []
        query.addBindValue(from_date)
        query.addBindValue(to_date)
        ok = query.exec()
        if not ok:
            return False, query.lastError().text(), []
        results = []
        while query.next():
            results.append(
                SummaryExportItemIn(
                    category_name=query.value(0),
                    payment_type=query.value(1),
                    commodity_name=query.value(2),
                    commodity_unit=query.value(3),
                    price_per_unit=query.value(4),
                    total_quantity=query.value(5),
                    total_price=query.value(6),
                )
            )
        return True, "", results

    @staticmethod
    def load_export_data_out(
        db_connection: QSqlDatabase, from_date: str, to_date: str
    ) -> tuple[bool, str, list[SummaryExportItemOut]]:
        query = QSqlQuery(db_connection)
        if not query.prepare(SUMMARY_QUERY_OUT):
            return False, query.lastError().text(), []
        query.addBindValue(from_date)
        query.addBindValue(to_date)
        ok = query.exec()
        if not ok:
            return False, query.lastError().text(), []
        results = []
        while query.next():
            results.append(
                SummaryExportItemOut(
                    category_name=query.value(0),
                    commodity_name=query.value(1),
                    commodity_unit=query.value(2),
                    total_quantity=query.value(3),
                )
            )
        return True, "", results
