from typing import TYPE_CHECKING

from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.text_file_handler import TextFileHandler

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.notes_widget import NotesWidget


class NotesController:
    def __init__(self, notes_widget: "NotesWidget") -> None:
        self.notes_widget = notes_widget

    def load_notes(self) -> None:
        ok, notes = TextFileHandler.load_document("toolbar_notes.txt")
        if not ok:
            self.notes_widget.status_bar.show_message("LOAD_NOTES_FAILED")
        self.notes_widget.permanent_notes_edit.setPlainText(notes)

    @classmethod
    def save_notes(cls) -> None:
        if not TextFileHandler.save_document("toolbar_notes.txt", cls.notes_widget.get_permanent_notes()):
            ErrorHandler.handle_error("Save notes failed", "app", "warning")