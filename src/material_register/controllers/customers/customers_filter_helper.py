class CustomersFilterHelper:

    @staticmethod
    def get_filter(text: str) -> str:
        text = CustomersFilterHelper.escape(text)
        conditions = []
        for field in [
            "company_normalized",
            "first_name_normalized",
            "last_name_normalized",
            "document_number",
            "address_normalized",
        ]:
            conditions.append(f"{field} LIKE '%{text}%'")
        return " OR ".join(conditions)

    @staticmethod
    def escape(text: str) -> str:
        return text.replace("'", "''")