from PySide6.QtSql import QSqlDatabase, QSqlTableModel


class BaseSqlTableModel(QSqlTableModel):
    def __init__(self, db: QSqlDatabase, parent=None) -> None:
        super().__init__(parent, db)

    def _find_row_by_id(self, customer_id: int) -> int:
        id_column = self.fieldIndex("id")
        for row in range(self.rowCount()):
            index = self.index(row, id_column)
            if self.data(index) == customer_id:
                return row
        return -1

    def _rollback_and_fail(self) -> bool:
        self.revertAll()
        return False
