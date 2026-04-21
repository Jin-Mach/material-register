from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from src.material_register.ui.widgets.side_panel import SidePanel
from src.material_register.ui.widgets.stacked_widget import StackedWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(900, 600)
        self.setCentralWidget(self.create_ui())
        self.create_connection()
        self._centered = False

    def create_ui(self) -> QWidget:
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        self.side_panel = SidePanel(self)
        self.stacked_widget = StackedWidget(self)
        main_layout.addWidget(self.side_panel)
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        return central_widget

    def create_connection(self) -> None:
        buttons_map = {
            self.stacked_widget.register_widget.actions_widget.add_action_button: 0
        }
        for button, index in buttons_map.items():
            button.clicked.connect(lambda i=index: self.stacked_widget.setCurrentIndex(i))

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if self._centered:
            return
        self._centered = True
        screen = self.screen()
        geometry = screen.availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(geometry.center())
        self.move(frame.topLeft())
