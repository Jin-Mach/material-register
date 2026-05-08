from dataclasses import fields

from PySide6.QtSql import QSqlDatabase, QSqlTableModel

from material_register.db.models.base_sql_table_model import BaseSqlTableModel
from material_register.domain.customers_dataclass import Customer


class CustomersModel(BaseSqlTableModel):
    def __init__(self, database: QSqlDatabase, parent=None) -> None:
        super().__init__(database, parent)
        self.setTable("customers")
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.setFilter(CustomersModel._basic_filter())
        self.select()

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

    @staticmethod
    def _basic_filter() -> str:
        return "active = 1"