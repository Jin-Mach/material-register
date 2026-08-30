from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.db.queries.export_queries.transactions_export_queries import (
    TransactionsExportQueries,
)
from material_register.domain.export_dataclass.transactions_dataclass import (
    TransactionsExportDay,
)
from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler
from material_register.services.export.excel.transactions_export.transactions_workbook import (
    TransactionsWorkbook,
)
from material_register.utils.date_filters import parse_date
from material_register.utils.system import is_disk_writable


class TransactionsExportWorker(QObject):
    finished = Signal()
    no_export_data = Signal(str)
    export_started = Signal()
    error = Signal(str)

    def __init__(
        self,
        export_settings: dict[str, Path | str | int | None | bool],
        export_texts: dict[str, dict[str, str]],
    ) -> None:
        super().__init__()
        self.export_settings = export_settings
        self.export_path = self.export_settings["export_path"]
        self.export_texts = export_texts
        self.transactions_texts = self.export_texts.get("TransactionsSheet", {})
        self.db_connection = None

    @Slot()
    def run(self) -> None:
        try:
            from_date = self.export_settings["from_date"]
            to_date = self.export_settings["to_date"]
            customer_id = self.export_settings["customer_id"]
            ok, error, self.db_connection = DbInit.thread_connection(
                "transactions_export_connection"
            )
            if not ok:
                self.error.emit(error)
                return
            in_ok, in_error, in_data = TransactionsExportQueries.load_export_data(
                self.db_connection, from_date, to_date, customer_id, TRANSFER_IN
            )
            if not in_ok:
                self.no_export_data.emit(in_error)
                return
            out_ok, out_error, out_data = TransactionsExportQueries.load_export_data(
                self.db_connection, from_date, to_date, customer_id, TRANSFER_OUT
            )
            if not out_ok:
                self.no_export_data.emit(out_error)
            transfer_in, transfer_out = self.export_settings.get("transfer_type", (TRANSFER_IN, None))
            if transfer_in is not None and not in_data:
                self.no_export_data.emit("NO_DATA")
                return
            if transfer_out is not None and not out_data:
                self.no_export_data.emit("NO_DATA")
                return
            self.export_started.emit()
            split_by_month = self.export_settings.get("split_by_month", True)
            if not split_by_month:
                ok, export_path = self._create_non_split_exports(in_data, out_data)
                if not ok:
                    self.error.emit(f"Export path {export_path} is not writable")
                    return
            else:
                ok, export_path = self._create_split_exports(in_data, out_data)
                if not ok:
                    self.error.emit(f"Export path {export_path} is not writable")
                    return
            self.finished.emit()
        except Exception as e:
            ErrorHandler.handle_error(e, "export", "error")
            self.error.emit(f"Export failed: {e}")

    def _create_non_split_exports(
        self,
        in_data: list[TransactionsExportDay],
        out_data: list[TransactionsExportDay],
    ) -> tuple[bool, Path]:
        export_path = self.export_path
        for transfer_type, data in ((TRANSFER_IN, in_data), (TRANSFER_OUT, out_data)):
            if not data:
                continue
            transfer_in, transfer_out = self.export_settings.get(
                "transfer_type", (TRANSFER_IN, None)
            )
            if (
                transfer_type == TRANSFER_IN
                and transfer_in is None
                or transfer_type == TRANSFER_OUT
                and transfer_out is None
            ):
                continue
            workbook = TransactionsWorkbook.create_workbook(
                self.export_settings,
                self.transactions_texts,
                data,
                transfer_type,
            )
            transfer_text = self.transactions_texts.get(transfer_type, transfer_type)
            export_path = self.export_path / f"{transfer_text}.xlsx"
            if not is_disk_writable(export_path.parent):
                return False, export_path
            workbook.save(export_path)
        return True, export_path

    def _create_split_exports(
        self,
        in_data: list[TransactionsExportDay],
        out_data: list[TransactionsExportDay],
    ) -> tuple[bool, Path]:
        export_path = self.export_path
        for transfer_type, data in ((TRANSFER_IN, in_data), (TRANSFER_OUT, out_data)):
            if not data:
                continue
            transfer_in, transfer_out = self.export_settings.get(
                "transfer_type", (TRANSFER_IN, None)
            )
            if (
                transfer_type == TRANSFER_IN
                and transfer_in is None
                or transfer_type == TRANSFER_OUT
                and transfer_out is None
            ):
                continue
            data_months_map = TransactionsExportWorker._split_data_by_month(data)
            for month, transactions in data_months_map.items():
                workbook = TransactionsWorkbook.create_workbook(
                    self.export_settings,
                    self.transactions_texts,
                    transactions,
                    transfer_type,
                )
                transfer_text = f"{self.transactions_texts.get(transfer_type, transfer_type)}_{month:02d}"
                export_path = self.export_path / f"{transfer_text}.xlsx"
                if not is_disk_writable(export_path.parent):
                    return False, export_path
                workbook.save(export_path)
        return True, export_path

    @staticmethod
    def _split_data_by_month(data: list[TransactionsExportDay]) -> dict:
        months_map = {}
        for transaction_day in data:
            transaction_date = transaction_day.transaction_date
            transaction_month = parse_date(transaction_date).month
            if not transaction_month in months_map:
                months_map[transaction_month] = [transaction_day]
            else:
                months_map[transaction_month].append(transaction_day)
        return months_map
