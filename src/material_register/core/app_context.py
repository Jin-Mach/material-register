from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMainWindow

if TYPE_CHECKING:
    from material_register.controllers.time_controller import TimeController


class AppContext:
    MAIN_WINDOW: QMainWindow | None = None
    TIME_CONTROLLER: "TimeController | None" = None

    @classmethod
    def set_main_window(cls, main_window: QMainWindow) -> None:
        cls.MAIN_WINDOW = main_window
        if cls.TIME_CONTROLLER is not None:
            cls.TIME_CONTROLLER.init_controller()
