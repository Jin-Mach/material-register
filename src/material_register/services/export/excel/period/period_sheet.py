from pathlib import Path
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Font, Protection

from material_register.domain.export_dataclass import ExportItemIn, ExportItemOut
from material_register.ui.helpers.formating_utils import format_date_range_to_locale


class PeriodSheet:
    START_ROW = 1
    LAST_COLUMN = 8

    TITLE_FONT_SIZE = 12
    DEFAULT_FONT_SIZE = 10

    TITLE_ROW_HEIGHT = 20
    DEFAULT_ROW_HEIGHT = 15

    ERROR_TEXT = "[N/A]"

    @staticmethod
    def create_sheet(sheet: Worksheet, export_settings: dict[str, Path | str | float | bool],
                     export_texts: dict[str, str],
                     data_in: list[ExportItemIn], out_data: list[ExportItemOut]) -> Worksheet:
        #print("in data:", data_in)
        #print("out data:", out_data)
        row = PeriodSheet.START_ROW
        row = PeriodSheet._create_header(sheet, row, PeriodSheet.LAST_COLUMN, export_settings, export_texts)
        sheet.freeze_panes = f"A{row}"
        sheet.protection.enable()
        return sheet

    @staticmethod
    def _create_header(sheet: Worksheet, row: int, last_column: int,
                       export_settings: dict[str, Path | str | float | bool],
                       export_texts: dict[str, str]) -> int:
        cell = sheet.cell(row=row, column=1, value=export_texts.get("titleText", PeriodSheet.ERROR_TEXT))
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, font_size=PeriodSheet.TITLE_FONT_SIZE, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.TITLE_ROW_HEIGHT
        PeriodSheet._cell_lock(cell)
        row += 1
        range_text = export_texts.get("rangeText", PeriodSheet.ERROR_TEXT)
        cell = sheet.cell(row, column=1, value=range_text)
        PeriodSheet._cell_alignment(cell, horizontal="left")
        PeriodSheet._cell_font(cell, PeriodSheet.DEFAULT_FONT_SIZE, bold=True)
        PeriodSheet._cell_lock(cell)
        period_value = PeriodSheet._get_period_range(export_settings.get("from_date", None),
                                                     export_settings.get("to_date", None))
        cell = sheet.cell(row, column=2, value=period_value)
        sheet.merge_cells(start_row=row, start_column=2, end_row=row, end_column=last_column // 2)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, PeriodSheet.DEFAULT_FONT_SIZE, bold=True)
        PeriodSheet._cell_lock(cell)
        branch_text = export_texts.get("branchText", PeriodSheet.ERROR_TEXT)
        cell = sheet.cell(row, column=(last_column // 2) + 1, value=branch_text)
        PeriodSheet._cell_alignment(cell, horizontal="left")
        PeriodSheet._cell_font(cell, PeriodSheet.DEFAULT_FONT_SIZE, bold=True)
        PeriodSheet._cell_lock(cell)
        branch_value = export_settings.get("branchNameLineEdit", PeriodSheet.ERROR_TEXT)
        cell = sheet.cell(row, column=(last_column // 2) + 2, value=branch_value)
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 2, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, PeriodSheet.DEFAULT_FONT_SIZE, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        PeriodSheet._cell_lock(cell)
        return row + 2

    @staticmethod
    def _cell_alignment(cell, horizontal: str = "center", vertical: str = "center") -> None:
        cell.alignment = Alignment(horizontal=horizontal, vertical=vertical, wrap_text=True)

    @staticmethod
    def _cell_font(cell, font_size: int | None = None, bold: bool = False) -> None:
        if font_size is None:
            font_size = PeriodSheet.DEFAULT_FONT_SIZE
        cell.font = Font(size=font_size, bold=bold)

    @staticmethod
    def _cell_lock(cell) -> None:
        cell.protection = Protection(locked=True)

    @staticmethod
    def _cell_unlock(cell) -> None:
        cell.protection = Protection(locked=False)

    @staticmethod
    def _get_period_range(from_date: str | None, to_date: str | None) -> str:
        if from_date is None or to_date is None:
            return PeriodSheet.ERROR_TEXT
        return format_date_range_to_locale(from_date, to_date)