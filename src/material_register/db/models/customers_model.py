from dataclasses import fields
from typing import Any

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlRecord, QSqlTableModel

from material_register.db.models.base_sql_table_model import BaseSqlTableModel
from material_register.domain.customers_dataclass import Customer
from material_register.ui.setup.ui_icons import UiIcons


class CustomersModel(BaseSqlTableModel):
    def __init__(self, database: QSqlDatabase, parent=None) -> None:
        super().__init__(database, parent)
        self.database = database
        self.setTable("customers")
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self.select()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            record = self.record(index.row())
            if column == self.fieldIndex("company"):
                return self._set_company_column(record)
            if column == self.fieldIndex("active"):
                return ""
            return super().data(index, role)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.DecorationRole and column == self.fieldIndex("active"):
            record = self.record(index.row())
            if record.value("active") == 1:
                return UiIcons.ACTIVE_ICON
            else:
                return UiIcons.INACTIVE_ICON
        if role == Qt.ItemDataRole.UserRole:
            record = self.record(index.row())
            return record.value("id")
        return super().data(index, role)

    def add_customer(self, customer: Customer) -> bool:
        row = self.rowCount()
        self.insertRow(row)
        for field in fields(customer):
            if field.name in ("id", "created_at"):
                continue
            value = getattr(customer, field.name)
            if value == "":
                value = None
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
            if value == "":
                value = None
            column_index = self.fieldIndex(field.name)
            if column_index == -1:
                return self._rollback_and_fail()
            index = self.index(row, column_index)
            self.setData(index, value)
        if not self.submitAll():
            return self._rollback_and_fail()
        return True

    def set_active(self, customer_id: int, active: bool) -> bool:
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

    def get_customer_by_id(self, customer_id: int) -> Customer | None:
        row = self._find_row_by_id(customer_id)
        if row == -1:
            return None
        record = self.record(row)
        return Customer(
            id=record.value("id"),
            company=record.value("company") or None,
            first_name=record.value("first_name") or None,
            last_name=record.value("last_name") or None,
            document_number=record.value("document_number"),
            address=record.value("address"),
            notes=record.value("notes"),
            created_at=record.value("created_at"),
            active=record.value("active"),
            company_normalized=record.value("company_normalized"),
            first_name_normalized=record.value("first_name_normalized"),
            last_name_normalized=record.value("last_name_normalized"),
            address_normalized=record.value("address_normalized"),
        )

    def document_exists(self, document_number: str, ignored_id: int | None = None) -> bool:
        query = QSqlQuery(self.database)
        sql = "SELECT 1 FROM customers WHERE document_number = ?"
        if ignored_id is not None:
            sql += " AND id != ?"
        sql += " LIMIT 1"
        query.prepare(sql)
        query.addBindValue(document_number)
        if ignored_id is not None:
            query.addBindValue(ignored_id)
        if not query.exec():
            return False
        return query.next()

    def get_total_count(self) -> int:
        query = QSqlQuery(self.database)
        query.exec("SELECT COUNT(*) FROM customers")
        if query.next():
            return query.value(0)
        return 0

    @staticmethod
    def _set_company_column(record: QSqlRecord) -> str:
        company = record.value("company")
        if company:
            return company.capitalize()
        first = record.value("first_name") or ""
        last = record.value("last_name") or ""
        return f"{first.capitalize()} {last.capitalize()}".strip()