from PySide6.QtWidgets import QDialog, QWidget

from material_register.ui.dialogs.messagebox_dialog import MessageBoxDialog


class MessageBoxes:
    CONFIRM_TEXTS = {}

    @classmethod
    def setup_init(cls, confirm_texts: dict[str, str]) -> None:
        cls.CONFIRM_TEXTS = confirm_texts

    @classmethod
    def show_question(cls, parent: QWidget, question_key: str, informative_text: str | None = None) -> bool:
        texts = cls.CONFIRM_TEXTS.get(question_key, {})
        if not texts:
            return False
        dialog = MessageBoxDialog(parent)
        dialog.setup_icon("QUESTION")
        dialog.setup_texts(texts.get("TITLE", ""), texts.get("TEXT", ""), ok_button=texts.get("YES", "Yes"),
                           cancel_button=texts.get("NO", "No"), informative_text=informative_text)
        return dialog.exec() == QDialog.DialogCode.Accepted

    @classmethod
    def show_error(cls, parent: QWidget, error_key: str, icon_key: str=None) -> None:
        texts = cls.CONFIRM_TEXTS.get(error_key, {})
        if not texts:
            return
        dialog = MessageBoxDialog(parent)
        dialog.setup_icon(icon_key)
        dialog.setup_texts(texts.get("TITLE", ""), texts.get("TEXT", ""), cancel_button=texts.get("CLOSE", "Close"))
        dialog.exec()