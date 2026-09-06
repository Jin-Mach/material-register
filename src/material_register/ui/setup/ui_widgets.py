from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDoubleSpinBox,
    QLineEdit,
    QListView,
    QListWidget,
    QPlainTextEdit,
    QSpinBox,
    QTableView,
    QTableWidget,
    QTextBrowser,
    QTextEdit,
    QTimeEdit,
    QTreeView,
    QTreeWidget,
    QWidget,
)


from material_register.config.ui_constants import INTEGER_SUFFIXES


CONTEXT_MENU_WIDGETS = (
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDoubleSpinBox,
    QLineEdit,
    QListView,
    QListWidget,
    QPlainTextEdit,
    QSpinBox,
    QTableView,
    QTableWidget,
    QTextBrowser,
    QTextEdit,
    QTimeEdit,
    QTreeView,
    QTreeWidget,
)


def set_suffix_mode(spinbox: QDoubleSpinBox, suffix: str) -> None:
    if suffix in INTEGER_SUFFIXES:
        spinbox.setDecimals(0)
        spinbox.setSingleStep(1)
        spinbox.setValue(round(spinbox.value()))
    else:
        spinbox.setDecimals(1)
        spinbox.setSingleStep(0.1)


def disable_context_menu(widgets: list[QWidget], ignored_widgets: set[str] | None = None) -> None:
    if ignored_widgets is None:
        ignored_widgets = set()
    for widget in widgets:
        if isinstance(widget, CONTEXT_MENU_WIDGETS):
            if widget.objectName() not in ignored_widgets:
                widget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

def setup_text_edit(text_edit: QTextEdit, read_only: bool = False) -> None:
    text_edit.setReadOnly(read_only)
    text_edit.setAcceptRichText(False)
    text_edit.setAcceptDrops(False)
    text_edit.setUndoRedoEnabled(False)