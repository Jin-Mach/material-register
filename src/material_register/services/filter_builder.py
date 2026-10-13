from material_register.db.config.search_queries_constants import (
    SEARCH_PERIOD_QUERY,
    SEARCH_VALUE_QUERY,
)
from material_register.utils.date_filters import get_filter_range
from material_register.utils.normalizer import normalize_text


class FilterBuilder:
    @staticmethod
    def create_basic_filter(
        period_key: str | None, value: str
    ) -> tuple[str, list[str]]:
        query = ""
        params = []
        period_query_state = False
        if period_key is not None:
            from_date, to_date = get_filter_range(period_key)
            params.extend((from_date, to_date))
            query += SEARCH_PERIOD_QUERY
            period_query_state = True
        if value:
            value_query = SEARCH_VALUE_QUERY
            normalized_value = normalize_text(value)
            params.extend(
                (
                    f"%{value}%",
                    f"%{normalized_value}%",
                    f"%{normalized_value}%",
                    f"%{normalized_value}%",
                    f"%{normalized_value}%",
                )
            )
            if period_query_state:
                query += " AND " + value_query
            else:
                query += value_query
        where = "WHERE " + query
        return where, params
