from material_register.db.models.customers_models.customers_completer_model import (
    CustomersCompleterModel,
)
from material_register.db.models.customers_models.customers_model import CustomersModel
from material_register.db.models.inventory_models.inventory_history_model import (
    InventoryHistoryModel,
)
from material_register.db.models.inventory_models.inventory_model import InventoryModel
from material_register.db.models.transactions_models.transactions_load_model_in import (
    TransactionsLoadModelIn,
)
from material_register.db.models.transactions_models.transactions_load_model_out import (
    TransactionsLoadModelOut,
)
from material_register.init.db_init import DbInit
from material_register.providers.performance_provider import PerformanceProvider
from material_register.services.db_cache import DbCache
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_CRITICAL,
    LOGGER_DB,
)


class DataInit:
    customers_model: CustomersModel | None = None
    customers_completer_model: CustomersCompleterModel | None = None
    transactions_load_model_in: TransactionsLoadModelIn | None = None
    transactions_load_model_out: TransactionsLoadModelOut | None = None
    inventory_model: InventoryModel | None = None
    inventory_history_model: InventoryHistoryModel | None = None

    @classmethod
    def init_data(cls) -> tuple[bool, str]:
        start = PerformanceProvider.start()
        try:
            cls.customers_model = CustomersModel(DbInit.db_connection)
            ok, error = DbCache.setup_init(DbInit.db_connection)
            if not ok:
                ErrorHandler.handle_error(error, LOGGER_DB, LOG_LEVEL_CRITICAL)
                return False, "DATABASE_FAILED"
            cls.customers_completer_model = CustomersCompleterModel(
                DbCache.active_customers
            )
            cls.transactions_load_model_in = TransactionsLoadModelIn(
                DbInit.db_connection
            )
            cls.transactions_load_model_out = TransactionsLoadModelOut(
                DbInit.db_connection
            )
            cls.inventory_model = InventoryModel(DbInit.db_connection)
            cls.inventory_history_model = InventoryHistoryModel()
            return True, ""
        except Exception as e:
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_CRITICAL)
            return False, "DATABASE_FAILED"
        finally:
            PerformanceProvider.stop(start, "DATAINIT.init_data")
