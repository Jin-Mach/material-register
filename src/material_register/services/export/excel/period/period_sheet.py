from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Font, Protection

from material_register.domain.export_dataclass import ExportItemIn, ExportItemOut


class PeriodSheet:
    START_ROW = 1
    LAST_COLUMN = 8

    TITLE_FONT_SIZE = 15
    HEADER_FONT_SIZE = 12
    DEFAULT_FONT_SIZE = 10

    TITLE_ROW_HEIGHT = 25
    HEADER_ROW_HEIGHT = 20
    DEFAULT_ROW_HEIGHT = 15

    @staticmethod
    def create_sheet(sheet: Worksheet, data_in: list[ExportItemIn], out_data: list[ExportItemOut]) -> Worksheet:
        print("in data:", data_in)
        print("out data:", out_data)
        row = PeriodSheet.START_ROW
        row = PeriodSheet._create_header(sheet, row, PeriodSheet.LAST_COLUMN)
        sheet.freeze_panes = f"A{row}"
        sheet.protection.enable()
        return sheet

    @staticmethod
    def _create_header(sheet: Worksheet, row: int, last_column: int) -> int:
        cell = sheet.cell(row=row, column=1, value="material register")
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, font_size=PeriodSheet.TITLE_FONT_SIZE, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.TITLE_ROW_HEIGHT
        PeriodSheet._cell_lock(cell)
        row += 1
        cell = sheet.cell(row, column=1, value="period: 1.1.2000 - 3.12.2000")
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_column // 2)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, PeriodSheet.HEADER_FONT_SIZE, bold=True)
        PeriodSheet._cell_lock(cell)
        cell = sheet.cell(row, column=(last_column // 2) + 1, value="branch")
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 1, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, PeriodSheet.HEADER_FONT_SIZE, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.HEADER_ROW_HEIGHT
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