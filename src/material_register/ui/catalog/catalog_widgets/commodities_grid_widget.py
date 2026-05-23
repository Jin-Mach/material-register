from PySide6.QtGui import QResizeEvent, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel, QGroupBox

from material_register.domain.commodities_dataclass import Commodity
from material_register.ui.catalog.catalog_widgets.commodity_card_widget import CommodityCardWidget


class CommoditiesGridWidget(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setLayout(self._create_ui())
        self.commodities_cards = []

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.commodities_group_box = QGroupBox("Commodities")
        self.commodities_group_box.setObjectName("CommoditiesGroupBox")
        box_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        container.setLayout(self.grid_layout)
        self.scroll_area.setWidget(container)
        self.no_commodities_label = QLabel("No commodities")
        self.no_commodities_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box_layout.addWidget(self.scroll_area)
        box_layout.addWidget(self.no_commodities_label)
        self.commodities_group_box.setLayout(box_layout)
        main_layout.addWidget(self.commodities_group_box)
        return main_layout

    def set_commodities(self, commodities: list[Commodity]) -> None:
        self.commodities_cards = []
        if not commodities:
            self.scroll_area.setVisible(False)
            self.no_commodities_label.setVisible(True)
            self._reload_commodities()
            return
        for commodity in commodities:
            card = CommodityCardWidget(self)
            card.set_commodity_details(commodity)
            self.commodities_cards.append(card)
        self._reload_commodities()
        self.scroll_area.setVisible(True)
        self.no_commodities_label.setVisible(False)

    def _reload_commodities(self) -> None:
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._relayout()

    def _relayout(self) -> None:
        if not self.commodities_cards:
            return
        width = self.scroll_area.viewport().width()
        item_width = self.commodities_cards[0].sizeHint().width()
        columns = max(1, width // (item_width + 10))
        for index, card in enumerate(self.commodities_cards):
            row = index // columns
            column = index % columns
            self.grid_layout.addWidget(card, row, column)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._relayout()