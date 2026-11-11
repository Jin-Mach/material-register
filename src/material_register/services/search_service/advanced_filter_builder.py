from material_register.db.config.advanced_search_queries_constants import (
    ADVANCED_SEARCH_AMOUNT_EXPRESSION,
    ADVANCED_SEARCH_COLUMNS,
    ADVANCED_SEARCH_QUERY_GROUP_BY,
    HAVING_CLAUSE,
    MATERIAL_FILTER_AMOUNT,
    MATERIAL_FILTER_CATEGORY,
    MATERIAL_FILTER_COMMODITY,
    MATERIAL_FILTER_EXISTS_END,
    MATERIAL_FILTER_EXISTS_START,
    MATERIAL_FILTER_GROUP_BY,
    MATERIAL_FILTER_PRICE_PER_UNIT,
    MATERIAL_FILTER_TOTAL_PRICE,
    WHERE_CLAUSE,
)
from material_register.domain.advanced_search_dataclass import (
    AdvancedSearchDataclass,
    MaterialFiltersDataclass,
)
from material_register.ui.config.ui_constants import TRANSFER_IN


class AdvancedFilterBuilder:
    @staticmethod
    def create_advanced_filter(
        filters: list[AdvancedSearchDataclass],
        material_filters: MaterialFiltersDataclass,
        amount_having: bool = False,
        material_having: bool = False,
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
        if material_filters.filters:
            material_where, material_params = (
                AdvancedFilterBuilder._create_material_where_query(material_filters)
            )
            if where:
                where += " AND " + material_where
            else:
                where = WHERE_CLAUSE + " " + material_where
            params.extend(material_params)
        if having_filters:
            if amount_having:
                having, having_params = (
                    AdvancedFilterBuilder._create_amount_having_query(having_filters)
                )
            elif material_having:
                having, having_params = (
                    AdvancedFilterBuilder._create_material_having_query(having_filters)
                )
            else:
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
            elif (
                search_filter.column_name
                == ADVANCED_SEARCH_COLUMNS["customer_subject_type"]
            ):
                query = f"{search_filter.column_name} {search_filter.query}"
                where.append(query)
            else:
                query = f"{search_filter.column_name} {search_filter.query}"
                where.append(query)
                params.append(search_filter.value)
        return WHERE_CLAUSE + " " + " AND ".join(where), params

    @staticmethod
    def _create_material_where_query(
        material_filters: MaterialFiltersDataclass,
    ) -> tuple[str, list[int | float]]:
        where = []
        params = []
        for single_filter in material_filters.filters:
            filter_where = MATERIAL_FILTER_EXISTS_START
            filter_having = []
            filter_params = []
            if single_filter.category_id is not None:
                filter_where += " " + MATERIAL_FILTER_CATEGORY
                filter_params.append(single_filter.category_id)
            if single_filter.commodity_id is not None:
                filter_where += " " + MATERIAL_FILTER_COMMODITY
                filter_params.append(single_filter.commodity_id)
            if single_filter.amount_value is not None:
                filter_having.append(
                    MATERIAL_FILTER_AMOUNT.format(
                        operator=single_filter.amount_operator
                    )
                )
                filter_params.append(single_filter.amount_value)
            if single_filter.price_per_unit_value is not None:
                filter_having.append(
                    MATERIAL_FILTER_PRICE_PER_UNIT.format(
                        operator=single_filter.price_per_unit_operator
                    )
                )
                filter_params.append(single_filter.price_per_unit_value)
            if single_filter.total_price_value is not None:
                filter_having.append(
                    MATERIAL_FILTER_TOTAL_PRICE.format(
                        operator=single_filter.total_price_operator
                    )
                )
                filter_params.append(single_filter.total_price_value)
            filter_where += " " + MATERIAL_FILTER_GROUP_BY
            if filter_having:
                filter_where += " " + HAVING_CLAUSE + " " + " AND ".join(filter_having)
            filter_where += " " + MATERIAL_FILTER_EXISTS_END
            where.append(filter_where)
            params.extend(filter_params)
        if where:
            where_query = "(" + f" {material_filters.operator} ".join(where) + ")"
        else:
            where_query = ""
        return where_query, params

    @staticmethod
    def _create_having_query(
        filters: list[AdvancedSearchDataclass],
    ) -> tuple[str, list[str | int | float]]:
        having = []
        params = []
        for search_filter in filters:
            if search_filter.column_name == ADVANCED_SEARCH_COLUMNS["total"]:
                trans_query = (
                    f"{ADVANCED_SEARCH_COLUMNS['transaction_type']} = '{TRANSFER_IN}'"
                )
                query = f"{trans_query} AND {search_filter.column_name} {search_filter.query}"
                having.append(query)
                params.append(search_filter.value)
            else:
                query = f"{search_filter.column_name} {search_filter.query}"
                having.append(query)
                params.append(search_filter.value)
        return HAVING_CLAUSE + " " + " AND ".join(having), params

    @staticmethod
    def _create_amount_having_query(
        filters: list[AdvancedSearchDataclass],
    ) -> tuple[str, list[str | int | float]]:
        having = []
        params = []
        for search_filter in filters:
            if search_filter.column_name == ADVANCED_SEARCH_COLUMNS["total"]:
                query = ADVANCED_SEARCH_AMOUNT_EXPRESSION + " " + search_filter.query
            else:
                query = f"{search_filter.column_name} {search_filter.query}"
            having.append(query)
            params.append(search_filter.value)
        return (
            ADVANCED_SEARCH_QUERY_GROUP_BY
            + " "
            + HAVING_CLAUSE
            + " "
            + " AND ".join(having),
            params,
        )

    @staticmethod
    def _create_material_having_query(
        filters: list[AdvancedSearchDataclass],
    ) -> tuple[str, list[str | int | float]]:
        having = []
        params = []
        for search_filter in filters:
            if search_filter.column_name == ADVANCED_SEARCH_COLUMNS["total"]:
                query = (
                    f"{ADVANCED_SEARCH_COLUMNS['transaction_type']} = '{TRANSFER_IN}'"
                    f" AND {ADVANCED_SEARCH_AMOUNT_EXPRESSION} "
                    f"{search_filter.query}"
                )
            else:
                query = f"{search_filter.column_name} {search_filter.query}"
            having.append(query)
            params.append(search_filter.value)
        return (
            ADVANCED_SEARCH_QUERY_GROUP_BY
            + " "
            + HAVING_CLAUSE
            + " "
            + " AND ".join(having),
            params,
        )
