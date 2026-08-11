from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QDialog

from material_register.core.app_context import AppContext

if TYPE_CHECKING:
    from material_register.ui.dialogs.notification_dialog import NotificationDialog


def centre_dialog(dialog: QDialog) -> None:
    parent = QApplication.activeWindow()
    if parent:
        geometry = parent.frameGeometry()
    else:
        geometry = dialog.screen().availableGeometry()
    frame = dialog.frameGeometry()
    frame.moveCenter(geometry.center())
    dialog.move(frame.topLeft())

def get_notification_position(dialog: "NotificationDialog", margin: int = 10) -> QPoint | None:
    main_window = AppContext.MAIN_WINDOW
    if main_window is None:
        return None
    local_point = main_window.rect().bottomRight()
    global_point = main_window.mapToGlobal(local_point)
    x = global_point.x() - dialog.width() - margin
    y = global_point.y() - dialog.height() - margin
    return QPoint(x, y)