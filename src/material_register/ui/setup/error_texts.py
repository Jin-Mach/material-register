from PySide6.QtWidgets import QLabel


class ErrorTexts:
    ERROR_TEXTS = {}

    @classmethod
    def setup_init(cls, error_texts) -> None:
        cls.ERROR_TEXTS = error_texts

    @classmethod
    def set_error_text(cls, error_key: str, widget: QLabel) -> None:
        error_text = cls.ERROR_TEXTS.get(
            error_key, cls.ERROR_TEXTS.get("UNKNOWN_ERROR")
        )
        widget.setText(error_text)
