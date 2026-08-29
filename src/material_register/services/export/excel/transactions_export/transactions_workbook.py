from pathlib import Path

from openpyxl import Workbook

from material_register.domain.export_dataclass.transactions_dataclass import (
    TransactionsExportDay,
)


class TransactionsWorkbook:
    ERROR_TEXT = "N/A"

    @staticmethod
    def create_workbook(
        export_settings: dict[str, Path | str | float | bool],
        export_texts: dict[str, dict[str, str]],
        data_in: list[TransactionsExportDay],
        data_out: list[TransactionsExportDay],
    ) -> Workbook:
        workbook = Workbook()
        #workbook.remove(workbook.active)
        transactions_texts = export_texts.get("TransactionsSheet", {})
        print("transactions_texts", transactions_texts)
        return workbook
