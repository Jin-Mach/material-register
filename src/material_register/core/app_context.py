from PySide6.QtWidgets import QMainWindow


class AppContext:
    MAIN_WINDOW = None
    TIME_CONTROLLER = None

    @classmethod
    def set_main_window(cls, main_window: QMainWindow) -> None:
        cls.MAIN_WINDOW = main_window
        if cls.TIME_CONTROLLER is not None:
            cls.TIME_CONTROLLER.init_controller()
