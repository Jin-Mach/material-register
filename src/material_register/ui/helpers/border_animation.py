from PySide6.QtCore import QEvent, QObject, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget


class BorderAnimation(QWidget):
    finished = Signal()

    def __init__(
        self,
        widget: QWidget,
        speed: int = 5,
        interval: int = 16,
        color: QColor | str = "#FFE066",
        thickness: int = 2,
    ) -> None:
        super().__init__(widget)
        self.widget = widget
        self.speed = speed
        self.color = QColor(color)
        self.thickness = thickness
        self.timer = QTimer(self)
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self._update_position)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.widget.installEventFilter(self)
        self.progress = 0
        self.search_finished = False
        self.finished_state = False

    def start_animation(self) -> None:
        self.setGeometry(self.widget.rect())
        self.show()
        self.raise_()
        self.timer.start()

    def stop_animation(self) -> None:
        self.timer.stop()
        self.hide()

    def eventFilter(self, watched_widget: QObject, event: QEvent) -> bool:
        if watched_widget is self.widget and event.type() == QEvent.Type.Resize:
            self.setGeometry(self.widget.rect())
            self.update()
        return super().eventFilter(watched_widget, event)

    def _update_position(self) -> None:
        self.progress = min(self.progress + self.speed, self.width())
        self.update()
        if self.progress >= self.width():
            if self.search_finished:
                self.timer.stop()
                if not self.finished_state:
                    self.finished_state = True
                    self.finished.emit()
            else:
                self.progress = 0
                self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(self.color, self.thickness))
            y_axis = int(self.thickness // 2)
            painter.drawLine(0, y_axis, self.progress, y_axis)
        finally:
            painter.end()
