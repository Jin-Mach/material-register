from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, QVariantAnimation
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_icons import UiIcons
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.tools.right_toolbar_widgets.cash_balance_widget import (
    CashBalanceWidget,
)
from material_register.ui.tools.right_toolbar_widgets.database_backup_widget import (
    DatabaseBackupWidget,
)
from material_register.ui.tools.right_toolbar_widgets.notes_widget import NotesWidget

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class RightToolbarWidget(QWidget):
    WIDTH = 35
    BUTTON_SIZE = 28

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
        self.cash_balance_widget = CashBalanceWidget(self)
        self.database_backup_widget = DatabaseBackupWidget(self)
        self.buttons_container = QWidget()
        self.buttons_container.setObjectName("buttonsContainer")
        self.buttons_container.setFixedWidth(self.WIDTH)
        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(0, 5, 0, 5)
        buttons_layout.setSpacing(5)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.notes_button = QPushButton()
        self.notes_button.setObjectName("notesButton")
        self.notes_button.setFixedSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.notes_button.setCheckable(True)
        self.cash_balance_button = QPushButton()
        self.cash_balance_button.setObjectName("cashBalanceButton")
        self.cash_balance_button.setFixedSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.cash_balance_button.setCheckable(True)
        self.database_button = QPushButton()
        self.database_button.setObjectName("databaseButton")
        self.database_button.setFixedSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.database_button.setCheckable(True)
        buttons_layout.addWidget(self.notes_button)
        buttons_layout.addWidget(self.cash_balance_button)
        buttons_layout.addWidget(self.database_button)
        buttons_layout.addStretch()
        self.buttons_container.setLayout(buttons_layout)
        return main_layout

    def _setup_ui(self) -> None:
        self.tools_container.setVisible(False)
        self._setup_animation()
        self._setup_texts()
        self._setup_icons()
        self._setup_container()
        self.update_tools_max_width()

    def _setup_texts(self) -> None:
        widgets = [self.notes_button, self.cash_balance_button, self.database_button]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_icons(self) -> None:
        widgets = [self.notes_button, self.cash_balance_button, self.database_button]
        if not UiIcons.set_icons("tools", widgets, icon_size=24):
            ErrorHandler.handle_error(
                f"Icons load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = "ICONS_LOAD_FAILED"
            return

    def _setup_container(self) -> None:
        for widget in [
            self.notes_widget,
            self.cash_balance_widget,
            self.database_backup_widget,
        ]:
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            scroll_area.setWidget(widget)
            self.tools_container.addWidget(scroll_area)

    def _setup_animation(self) -> None:
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(300)
        self.animation.valueChanged.connect(self._update_animation)
        self.animation.finished.connect(self._animation_finished)

    def _create_connection(self) -> None:
        buttons_map = {
            self.notes_button: 0,
            self.cash_balance_button: 1,
            self.database_button: 2,
        }
        for button, index in buttons_map.items():
            button.clicked.connect(lambda _, i=index: self._set_container_widget(i))

    def _update_animation(self, value: object) -> None:
        width = int(value)
        splitter_width = self.main_window.splitter.width()
        self.main_window.splitter.setSizes([splitter_width - width, width])

    def _animate_tools(self, start: int, end: int) -> None:
        self.animation.stop()
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()

    def _animation_finished(self) -> None:
        if self.main_window.splitter.sizes()[1] == 0:
            self.tools_container.setVisible(False)

    def _set_container_widget(self, index: int) -> None:
        buttons_map = {
            0: self.notes_button,
            1: self.cash_balance_button,
            2: self.database_button,
        }
        button = buttons_map[index]
        if self.tools_container.isVisible():
            if self.tools_container.currentIndex() == index:
                self.main_window.tools_width = self.main_window.splitter.sizes()[1]
                self._animate_tools(self.main_window.tools_width, 0)
                button.setChecked(False)
                return
            self.tools_container.setCurrentIndex(index)
        else:
            self.tools_container.setCurrentIndex(index)
            self.tools_container.setVisible(True)
            self.update_tools_max_width()
            self._animate_tools(0, self.main_window.tools_width)
        for current_button in buttons_map.values():
            current_button.setChecked(current_button is button)
        widget = self.tools_container.currentWidget()
        if hasattr(widget, "activate_widget"):
            widget.activate_widget()

    def update_tools_max_width(self) -> None:
        self.tools_container.setMaximumWidth(self.main_window.splitter.width() // 2)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_tools_max_width()
