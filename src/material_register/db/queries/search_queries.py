from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.export_config.search_queries_constants import (
    SEARCH_QUERY_END,
    SEARCH_QUERY_START,
)
from material_register.domain.search_dataclass import SearchDataclass
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_CRITICAL, LOGGER_DB


class SearchQueries:
    @staticmethod
    def load_transactions(
        db_connection: QSqlDatabase,
    ) -> tuple[bool, list[SearchDataclass]]:
        query = QSqlQuery(db_connection)
        final_query = SearchQueries._get_final_query()
        if not query.exec(final_query):
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
    def _get_final_query() -> str:
        return f"{SEARCH_QUERY_START}\n{SEARCH_QUERY_END}"
