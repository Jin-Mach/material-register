from typing import TYPE_CHECKING

from PySide6.QtGui import QResizeEvent, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel, QGroupBox

from material_register.domain.commodities_dataclass import Commodity
from material_register.services.error_handler import ErrorHandler
from material_register.ui.catalog.catalog_widgets.commodity_card_widget import CommodityCardWidget
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.category_with_commodities_widget import CategoryWithCommoditiesWidget
    from material_register.controllers.catalog.catalog_controller import CatalogController


class CommoditiesGridWidget(QWidget):
    def __init__(self, category_with_commodities_widget: "CategoryWithCommoditiesWidget",
                 catalog_controller: "CatalogController") -> None:
        super().__init__(category_with_commodities_widget)
        self.category_with_commodities_widget = category_with_commodities_widget
        self.catalog_controller = catalog_controller
        self.setLayout(self._create_ui())
        self._setup_texts()
        self.commodities_cards = []

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.commodities_group_box = QGroupBox()
        self.commodities_group_box.setObjectName("commoditiesGroupBox")
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

    def _setup_texts(self)-> None:
        widgets = [self.commodities_group_box]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def set_commodities(self, commodities: list[Commodity]) -> None:
        self.commodities_cards = []
        card_texts = UiTexts.UI_TEXTS.get("CommodityCardWidget", {})
        if not commodities:
            self.scroll_area.setVisible(False)
            self.no_commodities_label.setVisible(True)
            self._reload_commodities()
            return
        for commodity in commodities:
            card = CommodityCardWidget(self)
            card.setup_texts(card_texts)
            card.set_commodity_details(commodity)
            card.create_connection(commodity, self.catalog_controller.update_commodity)
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