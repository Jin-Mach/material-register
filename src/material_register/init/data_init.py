from material_register.db.models.customers_completer_model import CustomersCompleterModel
from material_register.db.models.customers_model import CustomersModel
from material_register.db.models.transactions_load_model_in import TransactionsLoadModelIn
from material_register.db.models.transactions_load_model_out import TransactionsLoadModelOut
from material_register.init.db_init import DbInit
from material_register.services.db_cache import DbCache
from material_register.services.error_handler import ErrorHandler


class DataInit:
    customers_model: CustomersModel | None = None
    customers_completer_model: CustomersCompleterModel | None = None
    transactions_load_model_in: TransactionsLoadModelIn | None = None
    transactions_load_model_out: TransactionsLoadModelOut | None = None

    @classmethod
    def init_data(cls) -> tuple[bool, str]:
        try:
            cls.customers_model = CustomersModel(DbInit.db_connection)
            DbCache.setup_init(DbInit.db_connection)
            cls.customers_completer_model = CustomersCompleterModel(DbCache.active_customers)
            cls.transactions_load_model_in = TransactionsLoadModelIn(DbInit.db_connection)
            cls.transactions_load_model_out = TransactionsLoadModelOut(DbInit.db_connection)
            return True, ""
        except Exception as e:
            ErrorHandler.handle_error(e, "db", "critical")
            return False, "DATABASE_FAILED"