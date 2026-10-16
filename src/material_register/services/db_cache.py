from PySide6.QtSql import QSqlDatabase

from material_register.db.queries.category_queries import CategoryQueries
from material_register.db.queries.commodities_queries import CommoditiesQueries
from material_register.db.queries.customers_queries import CustomersQueries
from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity
from material_register.domain.customers_dataclass import Customer


class DbCache:
    db_connection: QSqlDatabase | None = None
    customers: list[Customer] = []
    active_customers: list[Customer] = []
    inactive_customers: list[Customer] = []
    categories: list[Category] = []
    commodities: list[Commodity] = []

    @classmethod
    def setup_init(cls, db_connection: QSqlDatabase) -> tuple[bool, str]:
        cls.db_connection = db_connection
        ok, error = cls.refresh_customers_data()
        if not ok:
            return False, error
        return cls.refresh_catalog_data()

    @classmethod
    def refresh_customers_data(cls) -> tuple[bool, str]:
        ok, error, customers = cls._get_customers(cls.db_connection)
        if not ok:
            return False, error
        cls.customers = customers
        cls.active_customers = cls._filter_active_customers()
        cls.inactive_customers = cls._filter_inactive_customers()
        return True, ""

    @classmethod
    def refresh_catalog_data(cls) -> tuple[bool, str]:
        ok, error, categories = cls._get_categories(cls.db_connection)
        if not ok:
            return False, error
        ok, error, commodities = cls._get_commodities(cls.db_connection)
        if not ok:
            return False, error
        cls.categories = categories
        cls.commodities = commodities
        return True, ""

    @classmethod
    def _get_customers(
        cls, db_connection: QSqlDatabase
    ) -> tuple[bool, str, list[Customer]]:
        return CustomersQueries.get_customers(db_connection)

    @classmethod
    def _filter_active_customers(cls) -> list[Customer]:
        active = []
        for customer in cls.customers:
            if customer.active == 1:
                active.append(customer)
        return active

    @classmethod
    def _filter_inactive_customers(cls) -> list[Customer]:
        inactive = []
        for customer in cls.customers:
            if customer.active == 0:
                inactive.append(customer)
        return inactive

    @classmethod
    def _get_categories(
        cls, db_connection: QSqlDatabase
    ) -> tuple[bool, str, list[Category]]:
        return CategoryQueries.get_categories(db_connection)

    @classmethod
    def _get_commodities(
        cls, db_connection: QSqlDatabase
    ) -> tuple[bool, str, list[Commodity]]:
        return CommoditiesQueries.get_commodities(db_connection)
