from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from material_register.domain.customers_dataclass import Customer


class CustomersCompleterModel(QStandardItemModel):
    def __init__(self, customers: list[Customer]) -> None:
        super().__init__()
        self._load_customers(customers)

    def _load_customers(self, customers: list[Customer]) -> None:
        for customer in customers:
            name, address = CustomersCompleterModel._format_customer(customer)
            item = QStandardItem()
            item.setData(f"{name} - {address}", Qt.ItemDataRole.DisplayRole)
            item.setData(name, Qt.ItemDataRole.UserRole + 10)
            item.setData(customer, Qt.ItemDataRole.UserRole)
            self.appendRow(item)

    def reload_customers(self, customers: list[Customer]) -> None:
        self.clear()
        self._load_customers(customers)

    def get_customer_by_text(self, name: str) -> Customer | None:
        customer = None
        for row in range(self.rowCount()):
            index = self.index(row, 0)
            if self.data(index, Qt.ItemDataRole.UserRole + 10) == name:
                customer = self.data(index, Qt.ItemDataRole.UserRole)
                break
        return customer

    @staticmethod
    def _format_customer(customer: Customer) -> tuple[str, str]:
        if customer.company:
            return customer.company, customer.address
        return f"{customer.first_name} {customer.last_name}", customer.address
