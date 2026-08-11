from PySide6.QtWidgets import QMainWindow


class AppContext:
    MAIN_WINDOW = None

    @classmethod
    def set_main_window(cls, main_window: QMainWindow) -> None:
        cls.MAIN_WINDOW = main_window
