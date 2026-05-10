from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlTableModel
from PySide6.QtWidgets import QTableView

# noinspection PyBroadException
class HeadersTexts:
    HEADERS_TEXTS = {}

    @classmethod
    def setup_init(cls, headers_texts: dict[str, dict[str, str]]) -> None:
        cls.HEADERS_TEXTS = headers_texts.copy()

    @classmethod
    def set_headers_text(cls, view: QTableView, model: QSqlTableModel) -> bool:
        try:
            db_columns = []
            for column in range(model.columnCount()):
                db_columns.append(model.record().fieldName(column))
            headers_text = cls.HEADERS_TEXTS.get(view.__class__.__name__, {})
            if not headers_text:
                return False
            for index, column_name in enumerate(db_columns):
                if column_name in headers_text:
                    model.setHeaderData(index, Qt.Orientation.Horizontal, headers_text[column_name])
            return True
        except Exception:
            return False