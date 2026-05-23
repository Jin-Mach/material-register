from PySide6.QtGui import QResizeEvent, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel

from material_register.domain.commodities_dataclass import Commodity
from material_register.ui.catalog.catalog_widgets.commodity_card_widget import CommodityCardWidget


class CommoditiesGridWidget(QWidget):
    CARD_WIDTH = 250
    CARD_HEIGHT = 150

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setLayout(self._create_ui())
        self.commodities_cards = []

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        self.grid_layout = QGridLayout()
        container.setLayout(self.grid_layout)
        self.scroll_area.setWidget(container)
        self.no_commodities_label = QLabel("No commodities")
        self.no_commodities_label.setObjectName("noCommoditiesLabel")
        self.no_commodities_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.no_commodities_label)
        return main_layout

    def set_commodities(self, commodities: list[Commodity]) -> None:
        self.commodities_cards = []
        if not commodities:
            self.no_commodities_label.show()
            self.scroll_area.hide()
            return
        for commodity in commodities:
            commodity_card = CommodityCardWidget(self)
            commodity_card.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
            commodity_card.set_commodity_details(commodity)
            self.commodities_cards.append(commodity_card)
        self._reload_commodities()
        self.no_commodities_label.hide()
        self.scroll_area.show()

    def _reload_commodities(self) -> None:
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._relayout()

    def _relayout(self) -> None:
        width = self.scroll_area.viewport().width()
        columns = max(1, width // (self.CARD_WIDTH + 10))
        for index, commodity in enumerate(self.commodities_cards):
            row = index // columns
            column = index % columns
            self.grid_layout.addWidget(commodity, row, column)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._relayout()