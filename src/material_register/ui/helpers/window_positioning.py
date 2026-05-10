from PySide6.QtWidgets import QDialog, QApplication


def centre_dialog(dialog: QDialog) -> None:
    parent = QApplication.activeWindow()
    if parent:
        geometry = parent.frameGeometry()
    else:
        geometry = dialog.screen().availableGeometry()
    frame = dialog.frameGeometry()
    frame.moveCenter(geometry.center())
    dialog.move(frame.topLeft())