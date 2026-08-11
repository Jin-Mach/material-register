from PySide6.QtSql import QSqlDatabase

from material_register.db.queries.category_queries import CategoryQueries
from material_register.db.queries.commodities_queries import CommoditiesQueries
from material_register.db.queries.customers_queries import CustomersQueries
from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity
from material_register.domain.customers_dataclass import Customer


class DbCache:
    db_connection = None
    customers = []
    active_customers = []
    inactive_customers = []
    categories = []
    commodities = []

    @classmethod
    def setup_init(cls, db_connection: QSqlDatabase) -> None:
        cls.db_connection = db_connection
        cls.refresh_catalog_data()

    @classmethod
    def refresh_catalog_data(cls) -> None:
        cls.customers = cls._get_customers(cls.db_connection)
        cls.active_customers = cls._filter_active_customers()
        cls.inactive_customers = cls._filter_inactive_customers()
        cls.categories = cls._get_categories(cls.db_connection)
        cls.commodities = cls._get_commodities(cls.db_connection)

    @classmethod
    def _get_customers(cls, db_connection: QSqlDatabase) -> list[Customer]:
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
    def _get_categories(cls, db_connection: QSqlDatabase) -> list[Category]:
        return CategoryQueries.get_categories(db_connection)

    @classmethod
    def _get_commodities(cls, db_connection: QSqlDatabase) -> list[Commodity]:
        return CommoditiesQueries.get_commodities(db_connection)
