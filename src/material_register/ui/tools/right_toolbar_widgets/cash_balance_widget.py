from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widget import RightToolbarWidget


class CashBalanceWidget(QWidget):
    def __init__(self, right_tool_bar_widget: "RightToolbarWidget") -> None:
        super().__init__(right_tool_bar_widget)
