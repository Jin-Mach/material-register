from typing import TYPE_CHECKING

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widget import RightToolbarWidget


class NotesWidget(QWidget):
    def __init__(self, right_toolbar_widget: "RightToolbarWidget") -> None:
        super().__init__(right_toolbar_widget)
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
        self.permanent_notes_edit.setFocus()
        self._update_button_states()

    def _create_permanent_notes(self) -> QGroupBox:
        permanent_group_box = QGroupBox("Permanent")
        permanent_layout = QVBoxLayout()
        self.permanent_notes_edit = QTextEdit()
        self.permanent_notes_edit.setObjectName("permanentNotesEdit")
        buttons_layout = QHBoxLayout()
        self.permanent_copy_button = QPushButton("Copy")
        self.permanent_copy_button.setObjectName("permanentCopyButton")
        self.permanent_delete_button = QPushButton("Delete")
        self.permanent_delete_button.setObjectName("permanentDeleteButton")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.permanent_copy_button)
        buttons_layout.addWidget(self.permanent_delete_button)
        permanent_layout.addWidget(self.permanent_notes_edit)
        permanent_layout.addLayout(buttons_layout)
        permanent_group_box.setLayout(permanent_layout)
        return permanent_group_box

    def _create_local_notes(self) -> QGroupBox:
        local_group_box = QGroupBox("Local")
        local_layout = QVBoxLayout()
        self.local_notes_edit = QTextEdit()
        self.local_notes_edit.setObjectName("localNotesEdit")
        buttons_layout = QHBoxLayout()
        self.local_copy_button = QPushButton("Copy")
        self.local_copy_button.setObjectName("localCopyButton")
        self.local_delete_button = QPushButton("Delete")
        self.local_delete_button.setObjectName("localDeleteButton")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.local_copy_button)
        buttons_layout.addWidget(self.local_delete_button)
        local_layout.addWidget(self.local_notes_edit)
        local_layout.addLayout(buttons_layout)
        local_group_box.setLayout(local_layout)
        return local_group_box

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

    def activate_widget(self) -> None:
        self.permanent_notes_edit.setFocus()
        self._update_button_states()

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
