from dataclasses import fields

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

from material_register.db.models.base_sql_table_model import BaseSqlTableModel
from material_register.domain.customers_dataclass import Customer


class CustomersModel(BaseSqlTableModel):
    def __init__(self, database: QSqlDatabase, parent=None) -> None:
        super().__init__(database, parent)
        self.database = database
        self.setTable("customers")
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.setFilter(CustomersModel._basic_filter())
        self.select()

    def data(self, index,  role = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
                if index.column() == self.fieldIndex("company"):
                    record = self.record(index.row())
                    company = record.value("company")
                    if company:
                        return company.capitalize()
                    first_name = record.value("first_name").capitalize()
                    last_name = record.value("last_name").capitalize()
                    return f"{first_name} {last_name}".strip()
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.FontRole:
            record = self.record(index.row())
            if record.value("company"):
                font = QFont()
                font.setBold(True)
                return font
        return super().data(index, role)

    def add_customer(self, customer: Customer) -> bool:
        row = self.rowCount()
        self.insertRow(row)
        for field in fields(customer):
            if field.name in ("id", "created_at"):
                continue
            value = getattr(customer, field.name)
            column_index = self.fieldIndex(field.name)
            if column_index == -1:
                return self._rollback_and_fail()
            index = self.index(row, column_index)
            self.setData(index, value)
        if not self.submitAll():
            return self._rollback_and_fail()
        return True

    def update_customer(self, customer_id: int, customer: Customer) -> bool:
        row = self._find_row_by_id(customer_id)
        if row == -1:
            return False
        for field in fields(customer):
            if field.name in ("id", "created_at"):
                continue
            value = getattr(customer, field.name)
            column_index = self.fieldIndex(field.name)
            if column_index == -1:
                return self._rollback_and_fail()
            index = self.index(row, column_index)
            self.setData(index, value)
        if not self.submitAll():
            return self._rollback_and_fail()
        return True

    def activate_handler(self, customer_id: int, active: bool = True) -> bool:
        row = self._find_row_by_id(customer_id)
        if row == -1:
            return False
        column_index = self.fieldIndex("active")
        if column_index == -1:
            return self._rollback_and_fail()
        index = self.index(row, column_index)
        self.setData(index, int(active))
        if not self.submitAll():
            return self._rollback_and_fail()
        return True

    def document_exists(self, document_number: str) -> bool:
        query = QSqlQuery(self.database)
        query.prepare("SELECT 1 FROM customers WHERE document_number = ? LIMIT 1")
        query.addBindValue(document_number)
        if not query.exec():
            return False
        return query.next()

    @staticmethod
    def _basic_filter() -> str:
        return "active = 1"