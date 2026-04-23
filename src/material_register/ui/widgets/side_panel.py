from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from src.material_register.ui.setup.texts_setup import TextsSetup

if TYPE_CHECKING:
    from src.material_register.ui.main_window import MainWindow


class SidePanel(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setLayout(self._create_ui())
        self._ui_setup()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.register_button = QPushButton()
        self.register_button.setObjectName("registerButton")
        main_layout.addWidget(self.register_button)
        main_layout.addStretch()
        return main_layout

    def _ui_setup(self) -> None:
        try:
            if not TextsSetup.set_ui_texts(self, [self.register_button]):
                print("No ui texts set", self.__class__.__name__)
        except Exception as e:
            print(e)