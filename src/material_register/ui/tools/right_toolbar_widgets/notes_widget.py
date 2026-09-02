from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtGui import QGuiApplication, Qt, QTextCursor
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from material_register.controllers.tools_controllers.notes_controller import NotesController
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_icons import UiIcons
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widget import RightToolbarWidget
    from material_register.ui.widgets.status_bar import StatusBar


class NotesWidget(QWidget):
    ICON_SIZE = 24

    def __init__(
        self, status_bar: "StatusBar", right_toolbar_widget: "RightToolbarWidget"
    ) -> None:
        super().__init__(right_toolbar_widget)
        self.status_bar = status_bar
        self.notes_controller = NotesController(self)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 5, 0, 5)
        permanent_notes = self._create_permanent_notes()
        local_notes = self._create_local_notes()
        main_layout.addWidget(permanent_notes)
        main_layout.addWidget(local_notes)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_icons()
        self.notes_controller.load_notes()
        self._setup_text_edits()
        self._update_button_states()
        self._set_cursor_position()

    def _create_permanent_notes(self) -> QGroupBox:
        permanent_group_box = QGroupBox()
        permanent_group_box.setObjectName("permanentGroupBox")
        permanent_layout = QVBoxLayout()
        self.permanent_notes_edit = QTextEdit()
        self.permanent_notes_edit.setObjectName("permanentNotesEdit")
        buttons_layout = QHBoxLayout()
        self.permanent_copy_button = QPushButton()
        self.permanent_copy_button.setObjectName("permanentCopyButton")
        self.permanent_delete_button = QPushButton()
        self.permanent_delete_button.setObjectName("permanentDeleteButton")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.permanent_copy_button)
        buttons_layout.addWidget(self.permanent_delete_button)
        permanent_layout.addWidget(self.permanent_notes_edit)
        permanent_layout.addLayout(buttons_layout)
        permanent_group_box.setLayout(permanent_layout)
        return permanent_group_box

    def _create_local_notes(self) -> QGroupBox:
        local_group_box = QGroupBox()
        local_group_box.setObjectName("localGroupBox")
        local_layout = QVBoxLayout()
        self.local_notes_edit = QTextEdit()
        self.local_notes_edit.setObjectName("localNotesEdit")
        buttons_layout = QHBoxLayout()
        self.local_copy_button = QPushButton()
        self.local_copy_button.setObjectName("localCopyButton")
        self.local_delete_button = QPushButton()
        self.local_delete_button.setObjectName("localDeleteButton")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.local_copy_button)
        buttons_layout.addWidget(self.local_delete_button)
        local_layout.addWidget(self.local_notes_edit)
        local_layout.addLayout(buttons_layout)
        local_group_box.setLayout(local_layout)
        return local_group_box

    def _setup_icons(self) -> None:
        self.permanent_copy_button.setIcon(UiIcons.COPY_ICON)
        self.permanent_copy_button.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self.permanent_delete_button.setIcon(UiIcons.DELETE_ICON)
        self.permanent_delete_button.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self.local_copy_button.setIcon(UiIcons.COPY_ICON)
        self.local_copy_button.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self.local_delete_button.setIcon(UiIcons.DELETE_ICON)
        self.local_delete_button.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_text_edits(self) -> None:
        edits = [self.permanent_notes_edit, self.local_notes_edit]
        for edit in edits:
            edit.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            edit.setAcceptRichText(False)
            edit.setAcceptDrops(False)
            edit.setUndoRedoEnabled(False)

    def _create_connection(self) -> None:
        self.permanent_notes_edit.textChanged.connect(self._update_button_states)
        self.local_notes_edit.textChanged.connect(self._update_button_states)
        self.permanent_copy_button.clicked.connect(
            lambda: NotesWidget._copy_notes_to_clipboard(self.permanent_notes_edit)
        )
        self.permanent_delete_button.clicked.connect(
            lambda: NotesWidget._delete_notes(self.permanent_notes_edit)
        )
        self.local_copy_button.clicked.connect(
            lambda: NotesWidget._copy_notes_to_clipboard(self.local_notes_edit)
        )
        self.local_delete_button.clicked.connect(
            lambda: NotesWidget._delete_notes(self.local_notes_edit)
        )

    def _set_cursor_position(self) -> None:
        cursor = self.permanent_notes_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.permanent_notes_edit.setTextCursor(cursor)
        self.permanent_notes_edit.setFocus()

    def activate_widget(self) -> None:
        self._update_button_states()
        self._set_cursor_position()

    def get_permanent_notes(self) -> str:
        return self.permanent_notes_edit.toPlainText().strip()

    def _update_button_states(self) -> None:
        self.permanent_copy_button.setEnabled(
            self.permanent_notes_edit.toPlainText() != ""
        )
        self.permanent_delete_button.setEnabled(
            self.permanent_notes_edit.toPlainText() != ""
        )
        self.local_copy_button.setEnabled(self.local_notes_edit.toPlainText() != "")
        self.local_delete_button.setEnabled(self.local_notes_edit.toPlainText() != "")

    @staticmethod
    def _copy_notes_to_clipboard(text_edit: QTextEdit) -> None:
        QGuiApplication.clipboard().setText(text_edit.toPlainText().strip())

    @staticmethod
    def _delete_notes(text_edit: QTextEdit) -> None:
        text_edit.clear()
