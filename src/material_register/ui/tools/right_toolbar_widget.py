from typing import TYPE_CHECKING

from PySide6.QtGui import Qt
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QStackedWidget,
)

from material_register.ui.tools.right_toolbar_widgets.notes_widget import NotesWidget

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class RightToolbarWidget(QWidget):
    WIDTH = 40
    TOOL_WIDTH = 300
    BUTTON_SIZE = 30

    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.tools_container = QStackedWidget()
        self.notes_widget = NotesWidget(self)
        buttons_container = QWidget()
        buttons_container.setFixedWidth(self.WIDTH)
        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.notes_button = QPushButton()
        self.notes_button.setFixedSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        buttons_layout.addWidget(self.notes_button)
        buttons_layout.addStretch()
        buttons_container.setLayout(buttons_layout)
        main_layout.addWidget(self.tools_container)
        main_layout.addWidget(buttons_container)
        return main_layout

    def _setup_ui(self) -> None:
        self.tools_container.setVisible(False)
        self._setup_container()

    def _setup_container(self) -> None:
        for widget in [self.notes_widget]:
            self.tools_container.addWidget(widget)

    def _create_connection(self) -> None:
        buttons_map = {self.notes_button: 0}
        for button, index in buttons_map.items():
            button.clicked.connect(lambda _, i=index: self._set_container_widget(i))

    def _set_container_widget(self, index: int) -> None:
        if self.tools_container.isVisible():
            self.tools_container.setVisible(False)
            return
        self.tools_container.setCurrentIndex(index)
        self.tools_container.setVisible(True)
