from PySide6.QtWidgets import QWidget, QMessageBox


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
        message_box = QMessageBox(parent)
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setWindowTitle(texts.get("TITLE", ""))
        message_box.setText(texts.get("TEXT", ""))
        if informative_text is not None:
            message_box.setInformativeText(informative_text)
        yes_button = message_box.addButton(texts.get("YES", "Yes"), QMessageBox.ButtonRole.YesRole)
        message_box.addButton(texts.get("NO", "No"), QMessageBox.ButtonRole.NoRole)
        message_box.exec()
        return message_box.clickedButton() == yes_button

    @classmethod
    def show_error(cls, parent: QWidget, error_key: str, icon: QMessageBox.Icon) -> None:
        texts = cls.CONFIRM_TEXTS.get(error_key, {})
        if not texts:
            return
        message_box = QMessageBox(parent)
        message_box.setIcon(icon)
        message_box.setWindowTitle(texts.get("TITLE", ""))
        message_box.setText(texts.get("TEXT", ""))
        message_box.addButton(texts.get("CLOSE", "Close"), QMessageBox.ButtonRole.AcceptRole)
        message_box.exec()