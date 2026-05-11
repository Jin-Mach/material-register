from PySide6.QtWidgets import QWidget, QMessageBox


class MessageBoxes:
    CONFIRM_TEXTS = {}

    @classmethod
    def setup_init(cls, confirm_texts: dict[str, str]) -> None:
        cls.CONFIRM_TEXTS = confirm_texts

    @classmethod
    def show_question(cls, parent: QWidget, question_key: str) -> bool:
        texts = cls.CONFIRM_TEXTS.get(question_key, {})
        if not texts:
            return False
        message_box = QMessageBox(parent)
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setWindowTitle(texts.get("TITLE", ""))
        message_box.setText(texts.get("TEXT", ""))
        yes_button = message_box.addButton(texts.get("YES", ""), QMessageBox.ButtonRole.YesRole)
        message_box.addButton(texts.get("NO", ""), QMessageBox.ButtonRole.NoRole)
        message_box.exec()
        return message_box.clickedButton() == yes_button