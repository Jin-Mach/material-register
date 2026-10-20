from material_register.db.config.advanced_search_queries_constants import (
    ADVANCED_SEARCH_COLUMNS,
    HAVING_CLAUSE,
    WHERE_CLAUSE,
)
from material_register.domain.adavanced_search_dataclass import AdvancedSearchDataclass


class AdvancedFilterBuilder:
    @staticmethod
    def create_advanced_filter(
        filters: list[AdvancedSearchDataclass],
    ) -> tuple[str, str, list[str | int | float]]:
        params = []
        where_filters = []
        having_filters = []
        where = ""
        having = ""
        for search_filter in filters:
            if search_filter.clause == WHERE_CLAUSE:
                where_filters.append(search_filter)
            elif search_filter.clause == HAVING_CLAUSE:
                having_filters.append(search_filter)
        if where_filters:
            where, where_params = AdvancedFilterBuilder._create_where_query(
                where_filters
            )
            params.extend(where_params)
        if having_filters:
            having, having_params = AdvancedFilterBuilder._create_having_query(
                having_filters
            )
            params.extend(having_params)
        return where, having, params

    @staticmethod
    def _create_where_query(
        filters: list[AdvancedSearchDataclass],
    ) -> tuple[str, list[str | int | float]]:
        where = []
        params = []
        for search_filter in filters:
            if (
                search_filter.column_name
                == ADVANCED_SEARCH_COLUMNS["transaction_created_at"]
            ):
                query = f"{search_filter.column_name} {search_filter.query}"
                where.append(query)
                params.append(search_filter.value[0])
                params.append(search_filter.value[1])
            else:
                query = f"{search_filter.column_name} {search_filter.query}"
                where.append(query)
                params.append(search_filter.value)
        return WHERE_CLAUSE + " " + " AND ".join(where), params

    @staticmethod
    def _create_having_query(
        filters: list[AdvancedSearchDataclass],
    ) -> tuple[str, list[str | int | float]]:
        having = []
        params = []
        for search_filter in filters:
            query = f"{search_filter.column_name} {search_filter.query}"
            having.append(query)
            params.append(search_filter.value)
        return HAVING_CLAUSE + " " + " AND ".join(having), params
