from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtSql import QSqlTableModel
from PySide6.QtWidgets import QTableView

# noinspection PyBroadException
class HeadersTexts:
    HEADERS_TEXTS = {}

    @classmethod
    def setup_init(cls, headers_texts: dict[str, dict[str, str]]) -> None:
        cls.HEADERS_TEXTS = headers_texts.copy()

    @classmethod
    def set_headers_text(cls, view: QTableView, model: QSqlTableModel | QStandardItemModel) -> bool:
        try:
            headers_text = cls.HEADERS_TEXTS.get(view.__class__.__name__, {})
            if not headers_text:
                return False
            if isinstance(model, QSqlTableModel):
                db_columns = []
                for column in range(model.columnCount()):
                    db_columns.append(model.record().fieldName(column))
                for index, column_name in enumerate(db_columns):
                    if column_name in headers_text:
                        model.setHeaderData(index, Qt.Orientation.Horizontal, headers_text[column_name])
            elif isinstance(model, QStandardItemModel):
                for column, text in enumerate(headers_text.values()):
                    model.setHeaderData(column, Qt.Orientation.Horizontal, text)
            return True
        except Exception:
            return False