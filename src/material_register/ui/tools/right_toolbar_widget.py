from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_icons import UiIcons
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.tools.right_toolbar_widgets.notes_widget import NotesWidget

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class RightToolbarWidget(QWidget):
    WIDTH = 50
    TOOL_WIDTH = 300
    BUTTON_SIZE = 30

    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.tools_container = QStackedWidget()
        self.notes_widget = NotesWidget(self.main_window.status_bar, self)
        buttons_container = QWidget()
        buttons_container.setFixedWidth(self.WIDTH)
        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.notes_button = QPushButton()
        self.notes_button.setObjectName("notesButton")
        self.notes_button.setFixedSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.notes_button.setCheckable(True)
        buttons_layout.addWidget(self.notes_button)
        buttons_layout.addStretch()
        buttons_container.setLayout(buttons_layout)
        main_layout.addWidget(self.tools_container)
        main_layout.addWidget(buttons_container)
        return main_layout

    def _setup_ui(self) -> None:
        self.tools_container.setVisible(False)
        self._setup_texts()
        self._setup_icons()
        self._setup_container()

    def _setup_texts(self) -> None:
        widgets = [self.notes_button]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_icons(self) -> None:
        widgets = [self.notes_button]
        if not UiIcons.set_icons("tools", widgets):
            ErrorHandler.handle_error(
                f"Icons load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = "ICONS_LOAD_FAILED"
            return

    def _setup_container(self) -> None:
        for widget in [self.notes_widget]:
            widget.setFixedWidth(self.TOOL_WIDTH)
            self.tools_container.addWidget(widget)

    def _create_connection(self) -> None:
        buttons_map = {self.notes_button: 0}
        for button, index in buttons_map.items():
            button.clicked.connect(lambda _, i=index: self._set_container_widget(i))

    def _set_container_widget(self, index: int) -> None:
        if self.tools_container.isVisible():
            self.tools_container.setVisible(False)
            self.notes_button.setChecked(False)
            return
        self.tools_container.setCurrentIndex(index)
        widget = self.tools_container.currentWidget()
        if hasattr(widget, "activate_widget"):
            widget.activate_widget()
        self.tools_container.setVisible(True)
        self.notes_button.setChecked(True)
