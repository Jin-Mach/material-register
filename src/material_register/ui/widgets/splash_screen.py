from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QApplication, QProgressBar, QVBoxLayout, QLabel


class SplashScreen(QWidget):
    def __init__(self, resources_path: Path) -> None:
        super().__init__()
        self.resources_path = resources_path
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = self._load_pixmap(self.__class__.__name__)
        if pixmap is not None:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            label = QLabel()
            label.setPixmap(pixmap)
            main_layout.addWidget(label)
        else:
            text_widget = QLabel()
            text_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_widget.setText("Checking application...")
            main_layout.addWidget(text_widget)
            main_layout.addWidget(SplashScreen._create_progress_bar())
        return main_layout

    def _load_pixmap(self, pixmap_name: str) -> QPixmap | None:
        image_path = self.resources_path / "images" / f"{pixmap_name}.jpg"
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            return pixmap
        return None

    @staticmethod
    def _create_progress_bar() -> QProgressBar:
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(0)
        progress_bar.setTextVisible(False)
        return progress_bar

    def _center_window(self) -> None:
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.center() - self.rect().center())

    def show_splash(self) -> None:
        self._center_window()
        self.show()