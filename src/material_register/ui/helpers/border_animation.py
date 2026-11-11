from PySide6.QtCore import QEvent, QObject, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget


class BorderAnimation(QWidget):
    finished = Signal()

    def __init__(
        self,
        widget: QWidget,
        speed: int = 8,
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

    def eventFilter(self, watched_widget: QObject, event: QEvent) -> bool:
        if watched_widget is self.widget and event.type() == QEvent.Type.Resize:
            self.setGeometry(self.widget.rect())
            self.update()
        return super().eventFilter(watched_widget, event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            border_rect = QRectF(self.rect()).adjusted(
                self.thickness / 2,
                self.thickness / 2,
                -self.thickness / 2,
                -self.thickness / 2,
            )
            border_path = QPainterPath()
            border_path.addRoundedRect(border_rect, 4, 4)
            border_length = border_path.length()
            if self.width() == 0 or border_length == 0 or self.progress == 0:
                return
            head_distance = self.progress / self.width() * border_length
            segment_length = min(150, border_length)
            segment_start = max(0, head_distance - segment_length)
            segment_steps = 12
            points = []
            for step in range(segment_steps + 1):
                distance = segment_start + (
                    (head_distance - segment_start) * step / segment_steps
                )
                path_position = border_path.percentAtLength(distance)
                points.append(border_path.pointAtPercent(path_position))
            for step in range(segment_steps):
                fade = min((step + 1) / 3, (segment_steps - step) / 3, 1)
                segment_color = QColor(self.color)
                segment_color.setAlpha(round(self.color.alpha() * fade))
                painter.setPen(
                    QPen(
                        segment_color,
                        self.thickness,
                        Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.RoundCap,
                        Qt.PenJoinStyle.RoundJoin,
                    )
                )
                painter.drawLine(points[step], points[step + 1])
        finally:
            painter.end()
