from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.styles_constants import WARNING_STYLE
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    UI_SPACING,
)
from material_register.ui.search.search_widgets.search_detail_view import (
    SearchDetailView,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.search.search_widget import SearchWidget


class SearchDetailWidget(QWidget):
    def __init__(self, search_widget: "SearchWidget") -> None:
        super().__init__(search_widget)
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_widget = QTabWidget()
        self.info_tab = self._create_info_tab()
        self.items_tab = self._create_items_tab()
        self.tab_widget.addTab(self.info_tab, "")
        self.tab_widget.addTab(self.items_tab, "")
        main_layout.addWidget(self.tab_widget)
        return main_layout

    def _create_info_tab(self) -> QWidget:
        info_tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(0, 0, 0, 0)
        payment_layout = QHBoxLayout()
        payment_layout.setContentsMargins(0, 0, 0, 0)
        self.payment_info = QLabel()
        self.payment_info.setObjectName("paymentInfo")
        self.payment_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.is_invoiced_checkbox = QCheckBox()
        self.is_invoiced_checkbox.setObjectName("isInvoicedCheckBox")
        payment_layout.addStretch()
        payment_layout.addWidget(self.payment_info)
        payment_layout.addSpacing(20)
        payment_layout.addWidget(self.is_invoiced_checkbox)
        payment_layout.addStretch()
        info_content_layout = QHBoxLayout()
        info_content_layout.setSpacing(UI_SPACING)
        customer_section = self._create_customer_section()
        notes_section = self._create_notes_section()
        info_content_layout.addWidget(customer_section)
        info_content_layout.addWidget(notes_section, 1)
        main_layout.addLayout(payment_layout)
        main_layout.addLayout(info_content_layout, 1)
        info_tab.setLayout(main_layout)
        return info_tab

    def _create_customer_section(self) -> QGroupBox:
        self.customer_group_box = QGroupBox()
        self.customer_group_box.setObjectName("customerGroupBox")
        self.customer_group_box.setFixedWidth(400)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        form_layout = QFormLayout()
        form_layout.setFormAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.customer_name_label = QLabel()
        self.customer_name_label.setObjectName("customerNameLabel")
        self.customer_name = QLabel()
        self.document_number_label = QLabel()
        self.document_number_label.setObjectName("documentNumberLabel")
        self.customer_document = QLabel()
        self.customer_address_label = QLabel()
        self.customer_address_label.setObjectName("addressLabel")
        self.address_label = QLabel()
        form_layout.addRow(self.customer_name_label, self.customer_name)
        form_layout.addRow(self.document_number_label, self.customer_document)
        form_layout.addRow(self.customer_address_label, self.address_label)
        main_layout.addLayout(form_layout)
        self.customer_group_box.setLayout(main_layout)
        return self.customer_group_box

    def _create_notes_section(self) -> QGroupBox:
        self.notes_group_box = QGroupBox()
        self.notes_group_box.setObjectName("notesGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        self.notes_label = QLabel()
        self.notes_label.setObjectName("notesLabel")
        self.notes_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.notes_label.setWordWrap(True)
        main_layout.addWidget(self.notes_label)
        self.notes_group_box.setLayout(main_layout)
        return self.notes_group_box

    def _create_items_tab(self) -> QWidget:
        items_tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_view = SearchDetailView(self)
        main_layout.addWidget(self.detail_view)
        items_tab.setLayout(main_layout)
        return items_tab

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_check_box()
        self._setup_style()

    def _setup_texts(self) -> None:
        widgets = [
            self.is_invoiced_checkbox,
            self.customer_group_box,
            self.customer_name_label,
            self.document_number_label,
            self.customer_address_label,
            self.notes_group_box,
        ]
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.info_tab_text = ui_texts.get("infoTabText", "")
        self.items_tab_text = ui_texts.get("itemsTabText", "")
        self.tab_widget.setTabText(0, self.info_tab_text)
        self.tab_widget.setTabText(1, self.items_tab_text)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_check_box(self) -> None:
        self.is_invoiced_checkbox.setDisabled(True)
        self.is_invoiced_checkbox.hide()

    def _setup_style(self) -> None:
        font = QFont()
        font.setBold(True)
        self.payment_info.setFont(font)
        self.payment_info.setStyleSheet(WARNING_STYLE)
