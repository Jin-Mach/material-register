from PySide6.QtWidgets import QWidget, QMessageBox


class MessageBoxes:
    CONFIRM_TEXTS = {}

    @classmethod
    def setup_init(cls, confirm_texts: dict[str, str]) -> None:
        cls.CONFIRM_TEXTS = confirm_texts

    @classmethod
    def show_question(cls, parent: QWidget) -> bool:
        message_box = QMessageBox(parent)
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setWindowTitle(cls.CONFIRM_TEXTS.get("UPDATE_CUSTOMER_TITLE", "Edit user"))
        message_box.setText(cls.CONFIRM_TEXTS.get("UPDATE_CUSTOMER_TEXT", "Do you really want to edit the selected user?"))
        yes_button = message_box.addButton(cls.CONFIRM_TEXTS.get("UPDATE_CUSTOMER_YES", "Save"), QMessageBox.ButtonRole.YesRole)
        message_box.addButton(cls.CONFIRM_TEXTS.get("UPDATE_CUSTOMER_NO", "Cancel"), QMessageBox.ButtonRole.NoRole)
        message_box.exec()
        return message_box.clickedButton() == yes_button