from material_register.db.config.model_constants import NORMALIZED_COLUMNS


class CustomersFilterHelper:
    @staticmethod
    def get_filter(text: str) -> str:
        text = CustomersFilterHelper.escape(text)
        conditions = []
        for field in NORMALIZED_COLUMNS:
            conditions.append(f"{field} LIKE '%{text}%'")
        return " OR ".join(conditions)

    @staticmethod
    def escape(text: str) -> str:
        return text.replace("'", "''")
