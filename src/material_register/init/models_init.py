from material_register.db.models.customers_model import CustomersModel
from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler


class ModelsSetup:
    customers_model = None

    @classmethod
    def models_init(cls) -> tuple[bool, str]:
        try:
            cls.customers_model = CustomersModel(DbInit.db_connection)
            return True, ""
        except Exception as e:
            ErrorHandler.handle_error(e, "db", "critical")
            return False, "DATABASE_FAILED"