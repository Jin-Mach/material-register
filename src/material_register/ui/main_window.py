from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._centered = False

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
