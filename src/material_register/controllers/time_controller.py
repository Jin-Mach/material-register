from PySide6.QtCore import QObject, QTimer, Signal


class TimeController(QObject):
    HOURLY_INTERVAL = 3_600_000
    DELAY_INTERVAL = 10_000

    hourly_database_backup = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._hour_timer = None

    def init_controller(self) -> None:
        self.hour_interval()

    def hour_interval(self) -> None:
        self._hour_timer = QTimer(self)
        self._hour_timer.setInterval(self.HOURLY_INTERVAL)
        self._hour_timer.timeout.connect(self._emit_hourly_tasks)
        self._hour_timer.start()

    def _emit_hourly_tasks(self) -> None:
        tasks_map = {
            1: self.hourly_database_backup,
        }
        for delay, signal in tasks_map.items():
            QTimer.singleShot(self.DELAY_INTERVAL * delay, signal.emit)
