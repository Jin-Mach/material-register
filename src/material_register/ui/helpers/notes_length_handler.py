from PySide6.QtWidgets import QLabel, QTextEdit

from material_register.ui.helpers.styles import INVALID_INPUT_STYLE


def check_notes_length(
    notes_widget: QTextEdit, notes_label: QLabel, notes_text: str, notes_length: int
) -> None:
    text = notes_widget.toPlainText()
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    if len(text) > notes_length:
        notes_widget.setStyleSheet(INVALID_INPUT_STYLE)
        text = text[:notes_length]
    else:
        notes_widget.setStyleSheet("")
    if text != notes_widget.toPlainText():
        notes_widget.blockSignals(True)
        notes_widget.setPlainText(text)
        notes_widget.blockSignals(False)
        cursor = notes_widget.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        notes_widget.setTextCursor(cursor)
    notes_label.setText(f"{notes_text} {len(text)}/{notes_length}")
