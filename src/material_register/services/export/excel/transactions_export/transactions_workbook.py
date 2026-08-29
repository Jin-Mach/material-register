from pathlib import Path

from openpyxl import Workbook

from material_register.domain.export_dataclass.transactions_dataclass import (
    TransactionsExportDay,
)
from material_register.utils.date_filters import parse_date


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
        # workbook.remove(workbook.active)
        transactions_texts = export_texts.get("TransactionsSheet", {})
        from_date = parse_date(export_settings.get("from_date", None))
        to_date = parse_date(export_settings.get("to_date", None))
        if from_date.month != to_date.month:
            print("more months")
            split_by_month = export_settings.get("split_by_month", True)
            if split_by_month:
                print("split")
        return workbook
