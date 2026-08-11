from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.domain.customers_dataclass import Customer


class CustomersQueries:
    BASE_QUERY = """
            SELECT id, company, first_name, last_name, document_number, address, notes, created_at, active,
            company_normalized, first_name_normalized, last_name_normalized, address_normalized
            FROM customers
            """

    @staticmethod
    def get_customers(db_connection: QSqlDatabase) -> list[Customer]:
        query = QSqlQuery(db_connection)
        if not query.exec(CustomersQueries.BASE_QUERY):
            return []
        results = []
        while query.next():
            results.append(
                Customer(
                    id=query.value(0),
                    company=query.value(1),
                    first_name=query.value(2),
                    last_name=query.value(3),
                    document_number=query.value(4),
                    address=query.value(5),
                    notes=query.value(6),
                    created_at=query.value(7),
                    active=query.value(8),
                    company_normalized=query.value(9),
                    first_name_normalized=query.value(10),
                    last_name_normalized=query.value(11),
                    address_normalized=query.value(12),
                )
            )
        return results
