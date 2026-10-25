from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer
from PySide6.QtWidgets import QDialog, QWidget

from material_register.domain.adavanced_search_dataclass import AdvancedSearchDataclass
from material_register.domain.search_dataclass import SearchResultsDataclass
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_CRITICAL, LOGGER_DB
from material_register.ui.dialogs.advanced_search_dialog import AdvancedSearchDialog
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.helpers.border_animation import BorderAnimation
from material_register.workers.advanced_search_worker import AdvancedSearchWorker

if TYPE_CHECKING:
    from material_register.ui.search.search_widget import SearchWidget


class AdvancedSearchController(QObject):
    def __init__(self, search_widget: "SearchWidget") -> None:
        super().__init__(search_widget)
        self.search_widget = search_widget
        self.worker = None
        self.thread = None
        self.search_finished = True
        self.border_animation = None

    def start_advanced_filter(self) -> None:
        if self.thread is not None or self.worker is not None:
            return
        dialog = AdvancedSearchDialog(self.search_widget)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filters = dialog.get_advanced_filters()
            if not filters:
                return
            self.search_widget.search_actions_widget.set_search_buttons_state(True)
            self.border_animation = BorderAnimation(
                self.search_widget.transactions_group_box
            )
            self.border_animation.start_animation()
            self.search_finished = False
            self._start_worker(filters)

    def _start_worker(self, filters: list[AdvancedSearchDataclass]) -> None:
        self.thread = QThread()
        self.worker = AdvancedSearchWorker(filters)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._search_error)
        self.worker.finished.connect(self._search_ok)
        self.thread.start()

    def _search_error(self, error: str) -> None:
        self._clean_thread()
        QTimer.singleShot(100, lambda: self._finish_search(error=error))

    def _search_ok(self, results: SearchResultsDataclass) -> None:
        self._clean_thread()
        QTimer.singleShot(100, lambda: self._finish_search(results=results))

    def _check_finish(self) -> None:
        if self.border_animation is None:
            return
        self.border_animation.search_finished = True
        if self.border_animation.progress >= self.border_animation.width():
            self._cleanup_border_animation()
        else:
            self.border_animation.finished.connect(self._cleanup_border_animation)

    def _cleanup_border_animation(self) -> None:
        if self.border_animation is None:
            return
        self.border_animation.stop_animation()
        self.border_animation.deleteLater()
        self.border_animation = None
        self.search_widget.search_actions_widget.set_search_buttons_state(False)

    def _clean_thread(self) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _reset_variables(self) -> None:
        self.worker = None
        self.thread = None
        self.search_finished = True

    def _finish_search(
        self,
        results: SearchResultsDataclass | None = None,
        error: str | None = None,
    ) -> None:
        self.search_finished = True
        self._check_finish()
        self._reset_variables()
        if error is not None:
            AdvancedSearchController._handle_search_error(
                error, f"{self.__class__.__name__}._search_error", self.search_widget
            )
            return
        if results is None:
            AdvancedSearchController._handle_search_error(
                "SearchResultsDataclass is None",
                f"{self.__class__.__name__}._search_error",
                self.search_widget,
            )
            return
        if len(results.transactions) == 0:
            self.search_widget.search_actions_widget.search_line_edit.selectAll()
            self.search_widget.search_actions_widget.search_line_edit.setFocus()
            MessageBoxes.show_error(self.search_widget, "NO_RESULTS", "WARNING")
            return
        self.search_widget.search_actions_widget.reset_filters_widgets()
        self.search_widget.search_detail_widget.reset_data()
        self.search_widget.search_detail_widget.tab_widget.setCurrentIndex(0)
        self.search_widget.search_tab_widget.setCurrentIndex(0)
        transactions = results.transactions
        transactions_count = results.transactions_count
        transactions_amount = results.transactions_total_amount
        materials = results.materials
        self.search_widget.search_transactions_model.load_data(transactions)
        self.search_widget.set_count_text(len(transactions), transactions_count)
        self.search_widget.set_price_text(transactions_amount)
        self.search_widget.search_material_model.load_data(materials)

    def shut_down(self) -> None:
        if self.thread is None:
            return
        self.thread.quit()
        self.thread.wait()

    @staticmethod
    def _handle_search_error(
        error: str, method: str, parent: QWidget, error_key: str = "SEARCH_ERROR"
    ) -> None:
        if not error:
            error = f"Unknown search error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", LOGGER_DB, LOG_LEVEL_CRITICAL)
        ErrorDialog(parent).show_dialog(error_key, False)
