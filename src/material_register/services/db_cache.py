from PySide6.QtSql import QSqlDatabase

from material_register.db.queries.category_queries import CategoryQueries
from material_register.db.queries.commodities_queries import CommoditiesQueries
from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity


class DbCache:
    def __init__(self) -> None:
        self.db_connection = None
        self.categories = []
        self.commodities = []

    @classmethod
    def setup_init(cls, db_connection: QSqlDatabase) -> None:
        cls.db_connection = db_connection
        cls.refresh_catalog_data()

    @classmethod
    def refresh_catalog_data(cls) -> None:
        cls.categories = cls._get_categories(cls.db_connection)
        cls.commodities = cls._get_commodities(cls.db_connection)

    @classmethod
    def _get_categories(cls, db_connection: QSqlDatabase) -> list[Category]:
        return CategoryQueries.get_categories(db_connection)

    @classmethod
    def _get_commodities(cls, db_connection: QSqlDatabase) -> list[Commodity]:
        return CommoditiesQueries.get_commodities(db_connection)