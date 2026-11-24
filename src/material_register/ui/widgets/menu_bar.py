from typing import TYPE_CHECKING

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar

from material_register.services.db_cache import DbCache
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_WARNING, LOGGER_UI
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class MenuBar(QMenuBar):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.addMenu(self._setup_transactions_menu())
        self.addMenu(self._setup_export_menu())
        self.addMenu(self._setup_customers_menu())
        self.addMenu(self._setup_catalog_menu())
        self.addMenu(self._setup_tools_menu())
        self._setup_ui()
        self._create_connection()

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_widgets()

    def _setup_texts(self) -> None:
        menu = self.findChildren(QMenu)
        actions = self.findChildren(QAction)
        widgets = menu + actions
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _create_connection(self) -> None:
        self.add_commodity.aboutToShow.connect(self._setup_commodity_menu)
        self.add_transaction_in.triggered.connect(
            self.transactions_widget.add_transaction_in
        )
        self.add_transaction_out.triggered.connect(
            self.transactions_widget.add_transaction_out
        )
        self.run_summary_export.triggered.connect(
            self.summary_export_widget.start_export
        )
        self.run_transactions_export.triggered.connect(
            self.transactions_export_widget.start_export
        )
        self.add_customer.triggered.connect(self.customers_widget.add_customer)
        self.add_category.triggered.connect(self.catalog_widget.add_category)
        self.add_commodity.triggered.connect(self._add_commodity)

    def _add_commodity(self, action: QAction) -> None:
        selected_category = action.data()
        self.catalog_widget.add_commodity(selected_category)

    def _setup_widgets(self) -> None:
        self.transactions_widget = self.main_window.stacked_widget.transactions_widget
        export_widget = self.main_window.stacked_widget.export_widget
        self.summary_export_widget = export_widget.summary_export_widget
        self.transactions_export_widget = export_widget.transactions_export_widget
        self.customers_widget = self.main_window.stacked_widget.customers_widget
        self.catalog_widget = self.main_window.stacked_widget.catalog_widget

    def _setup_transactions_menu(self) -> QMenu:
        self.transactions_menu = QMenu(self)
        self.transactions_menu.setObjectName("transactionsMenu")
        self.add_transaction_in = QAction(self)
        self.add_transaction_in.setObjectName("addTransactionIn")
        self.add_transaction_out = QAction(self)
        self.add_transaction_out.setObjectName("addTransactionOut")
        self.transactions_menu.addAction(self.add_transaction_in)
        self.transactions_menu.addAction(self.add_transaction_out)
        return self.transactions_menu

    def _setup_export_menu(self) -> QMenu:
        self.export_menu = QMenu(self)
        self.export_menu.setObjectName("exportMenu")
        self.run_summary_export = QAction(self)
        self.run_summary_export.setObjectName("runSummaryExport")
        self.run_transactions_export = QAction(self)
        self.run_transactions_export.setObjectName("runTransactionsExport")
        self.export_menu.addAction(self.run_summary_export)
        self.export_menu.addAction(self.run_transactions_export)
        return self.export_menu

    def _setup_customers_menu(self) -> QMenu:
        self.customers_menu = QMenu(self)
        self.customers_menu.setObjectName("customersMenu")
        self.add_customer = QAction(self)
        self.add_customer.setObjectName("addCustomer")
        self.customers_menu.addAction(self.add_customer)
        return self.customers_menu

    def _setup_catalog_menu(self) -> QMenu:
        self.catalog_menu = QMenu(self)
        self.catalog_menu.setObjectName("catalogMenu")
        self.add_category = QAction(self)
        self.add_category.setObjectName("addCategory")
        self.add_commodity = QMenu(self)
        self.add_commodity.setObjectName("addCommodity")
        self.category_title = QAction(self)
        self.category_title.setObjectName("addCategoryTitle")
        self.category_title.setDisabled(True)
        self.catalog_menu.addAction(self.add_category)
        self.catalog_menu.addMenu(self.add_commodity)
        return self.catalog_menu

    def _setup_commodity_menu(self) -> None:
        self.add_commodity.clear()
        self.add_commodity.addAction(self.category_title)
        self.add_commodity.addSeparator()
        categories = DbCache.categories
        for category in sorted(categories, key=lambda cat: cat.name):
            action = QAction(self.add_commodity)
            action.setText(category.name)
            action.setData(category)
            self.add_commodity.addAction(action)

    def _setup_tools_menu(self) -> QMenu:
        self.tools_menu = QMenu(self)
        self.tools_menu.setObjectName("toolsMenu")
        self.export_logs_data = QAction(self)
        self.export_logs_data.setObjectName("exportLogsData")
        self.tools_menu.addAction(self.export_logs_data)
        return self.tools_menu
