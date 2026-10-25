from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.advanced_search_queries_constants import (
    ADVANCED_SEARCH_MATERIAL_QUERY_GROUP_BY,
    ADVANCED_SEARCH_MATERIAL_QUERY_ORDER_BY,
    ADVANCED_SEARCH_MATERIAL_QUERY_START,
    ADVANCED_SEARCH_QUERY_GROUP_BY,
    ADVANCED_SEARCH_QUERY_ORDER_BY,
    ADVANCED_SEARCH_QUERY_START,
    ADVANCED_SEARCH_TRANSACTIONS_AMOUNT_QUERY_START,
)
from material_register.domain.search_dataclass import MaterialDataclass, SearchDataclass
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_CRITICAL, LOGGER_DB


class AdvancedSearchQueries:
    @staticmethod
    def load_transactions(
        db_connection: QSqlDatabase,
        where: str,
        having: str,
        params: list[str | int | float],
    ) -> tuple[bool, list[SearchDataclass]]:
        query = QSqlQuery(db_connection)
        final_query = AdvancedSearchQueries._get_final_search_query(where, having)
        query.prepare(final_query)
        for param in params:
            query.addBindValue(param)
        if not query.exec():
            ErrorHandler.handle_error(
                query.lastError().text(), LOGGER_DB, LOG_LEVEL_CRITICAL
            )
            return False, []
        results = []
        while query.next():
            results.append(
                SearchDataclass(
                    transaction_id=query.value("transaction_id"),
                    transaction_type=query.value("transaction_type"),
                    transaction_created_at=query.value("transaction_created_at"),
                    payment_type=query.value("transaction_payment_type"),
                    is_invoiced=bool(query.value("transaction_is_invoiced")),
                    customer_id=query.value("customer_id"),
                    customer_document_number=query.value("customer_document_number"),
                    customer_address=query.value("customer_address"),
                    customer_name=query.value("customer_name"),
                    transaction_notes=query.value("transaction_notes"),
                    total=query.value("total"),
                    suffix=query.value("suffix") or None,
                )
            )
        return True, results

    @staticmethod
    def get_total_amount(
        db_connection: QSqlDatabase,
        where: str,
        having: str,
        params: list[str | int | float],
    ) -> tuple[bool, float]:
        query = QSqlQuery(db_connection)
        final_query = AdvancedSearchQueries._get_final_amount_query(where, having)
        query.prepare(final_query)
        for param in params:
            query.addBindValue(param)
        if not query.exec():
            ErrorHandler.handle_error(
                query.lastError().text(), LOGGER_DB, LOG_LEVEL_CRITICAL
            )
            return False, 0.0
        total_amount = 0.0
        if query.next():
            total_amount = query.value(0) or 0.0
        return True, total_amount

    @staticmethod
    def load_material(
        db_connection: QSqlDatabase,
        where: str,
        having: str,
        params: list[str | int | float],
    ) -> tuple[bool, list[MaterialDataclass]]:
        query = QSqlQuery(db_connection)
        final_query = AdvancedSearchQueries._get_final_material_query(where, having)
        query.prepare(final_query)
        for param in params:
            query.addBindValue(param)
        if not query.exec():
            ErrorHandler.handle_error(
                query.lastError().text(), LOGGER_DB, LOG_LEVEL_CRITICAL
            )
            return False, []
        results = []
        while query.next():
            results.append(
                MaterialDataclass(
                    query.value(0),
                    query.value(1),
                    query.value(2),
                    query.value(3),
                )
            )
        return True, results

    @staticmethod
    def _get_final_search_query(where: str, having: str) -> str:
        queries = [ADVANCED_SEARCH_QUERY_START]
        if where:
            queries.append(where)
        queries.append(ADVANCED_SEARCH_QUERY_GROUP_BY)
        if having:
            queries.append(having)
        queries.append(ADVANCED_SEARCH_QUERY_ORDER_BY)
        return " ".join(queries)

    @staticmethod
    def _get_final_amount_query(where: str, having: str) -> str:
        queries = [ADVANCED_SEARCH_TRANSACTIONS_AMOUNT_QUERY_START]
        if where:
            queries.append(where)
        if having:
            queries.append(having)
        queries.append(")")
        return " ".join(queries)

    @staticmethod
    def _get_final_material_query(where: str, having: str) -> str:
        queries = [ADVANCED_SEARCH_MATERIAL_QUERY_START]
        if where:
            queries.append(where)
        if having:
            queries.append(having)
        queries.append(")")
        queries.append(ADVANCED_SEARCH_MATERIAL_QUERY_GROUP_BY)
        queries.append(ADVANCED_SEARCH_MATERIAL_QUERY_ORDER_BY)
        return " ".join(queries)
