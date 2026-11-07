from PySide6.QtGui import QStandardItemModel


class MaterialFilterModel(QStandardItemModel):
    def __init__(self) -> None:
        super().__init__()
