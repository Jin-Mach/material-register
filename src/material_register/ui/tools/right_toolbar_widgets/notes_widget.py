from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widget import RightToolbarWidget


class NotesWidget(QWidget):
    WIDTH = 300

    def __init__(self, right_toolbar_widget: "RightToolbarWidget"):
        super().__init__(right_toolbar_widget)
        self.setFixedWidth(self.WIDTH)
