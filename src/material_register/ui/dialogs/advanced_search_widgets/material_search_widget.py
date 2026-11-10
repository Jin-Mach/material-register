from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListView,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from material_register.db.models.search_models.material_filter_model import (
    MaterialFilterModel,
)
from material_register.domain.adavanced_search_dataclass import (
    MaterialFiltersDataclass,
    MaterialSearchDataclass,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    UI_MARGINS_5,
    UI_SPACING,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.controllers.material_filter_controller import (
        MaterialFilterController,
    )
    from material_register.ui.dialogs.advanced_search_dialog import AdvancedSearchDialog


class MaterialSearchWidget(QWidget):
    AND_OPERATOR = "AND"
    OR_OPERATOR = "OR"

    def __init__(
        self,
        material_filter_controller: "MaterialFilterController",
        advanced_search_dialog: "AdvancedSearchDialog",
    ) -> None:
        super().__init__(advanced_search_dialog)
        self.material_filter_controller = material_filter_controller
        self.advanced_search_dialog = advanced_search_dialog
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(0, 0, 0, 0)
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(UI_SPACING)
        filters_layout.setContentsMargins(*UI_MARGINS_5)
        self.add_filter_button = QPushButton()
        self.add_filter_button.setObjectName("addFilterButton")
        self.update_filter_button = QPushButton()
        self.update_filter_button.setObjectName("updateFilterButton")
        self.delete_filter_button = QPushButton()
        self.delete_filter_button.setObjectName("deleteFilterButton")
        self.and_operator_radio_button = QRadioButton()
        self.and_operator_radio_button.setObjectName("andOperatorRadioButton")
        self.or_operator_radio_button = QRadioButton()
        self.or_operator_radio_button.setObjectName("orOperatorRadioButton")
        self.filters_list_view = QListView()
        buttons_layout = QHBoxLayout()
        self.reset_button = QPushButton()
        self.reset_button.setObjectName("resetButton")
        filters_layout.addWidget(self.add_filter_button)
        filters_layout.addWidget(self.update_filter_button)
        filters_layout.addWidget(self.delete_filter_button)
        filters_layout.addStretch()
        filters_layout.addWidget(self.and_operator_radio_button)
        filters_layout.addSpacing(UI_SPACING)
        filters_layout.addWidget(self.or_operator_radio_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
        main_layout.addLayout(filters_layout)
        main_layout.addWidget(self.filters_list_view, 1)
        main_layout.addLayout(buttons_layout)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_push_buttons()
        self._setup_radio_buttons()
        self._setup_listview()
        self._setup_property()
        self._update_reset_button_state()

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.add_filter_button.clicked.connect(
            self.material_filter_controller.add_filter
        )
        self.update_filter_button.clicked.connect(
            self.material_filter_controller.update_filter
        )
        self.delete_filter_button.clicked.connect(
            self.material_filter_controller.delete_filter
        )
        self.reset_button.clicked.connect(self._setup_default_states)
        self.filters_list_view.selectionModel().selectionChanged.connect(
            self._update_buttons_state
        )
        self.material_filter_model.rowsInserted.connect(self._update_reset_button_state)
        self.material_filter_model.rowsRemoved.connect(self._update_reset_button_state)
        self.material_filter_model.modelReset.connect(self._update_reset_button_state)

    def _setup_default_states(self) -> None:
        self._setup_push_buttons()
        self._setup_radio_buttons()
        self.material_filter_model.clear()

    def _setup_push_buttons(self) -> None:
        self.update_filter_button.setDisabled(True)
        self.delete_filter_button.setDisabled(True)

    def _setup_radio_buttons(self) -> None:
        self.and_operator_radio_button.setChecked(True)

    def _setup_listview(self) -> None:
        self.filters_list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.filters_list_view.setVerticalScrollMode(
            QListView.ScrollMode.ScrollPerPixel
        )
        self.filters_list_view.setAlternatingRowColors(True)
        self.material_filter_model = MaterialFilterModel()
        self.filters_list_view.setModel(self.material_filter_model)
        self.material_filter_controller.set_material_filter_model(
            self.material_filter_model
        )

    def _setup_property(self) -> None:
        self.and_operator_radio_button.setProperty("operator", self.AND_OPERATOR)
        self.or_operator_radio_button.setProperty("operator", self.OR_OPERATOR)

    def _update_buttons_state(self) -> None:
        selection = self.filters_list_view.currentIndex().isValid()
        self.update_filter_button.setDisabled(not selection)
        self.delete_filter_button.setDisabled(not selection)

    def _update_reset_button_state(self) -> None:
        disabled = True
        if self.material_filter_model.rowCount() > 0:
            disabled = False
        self.reset_button.setDisabled(disabled)
        self.advanced_search_dialog.update_search_button_state(
            material_state=not disabled
        )

    def _get_operator(self) -> str:
        for radiobutton in [
            self.and_operator_radio_button,
            self.or_operator_radio_button,
        ]:
            if radiobutton.isChecked():
                return radiobutton.property("operator")
        return self.AND_OPERATOR

    def _get_model_filters(self) -> list[MaterialSearchDataclass]:
        filters_data = []
        for row in range(self.material_filter_model.rowCount()):
            item = self.material_filter_model.item(row)
            filters_data.append(item.data(Qt.ItemDataRole.UserRole))
        return filters_data

    def get_filters_data(self) -> MaterialFiltersDataclass:
        return MaterialFiltersDataclass(
            operator=self._get_operator(),
            filters=self._get_model_filters(),
        )
