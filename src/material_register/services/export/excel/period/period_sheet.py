from pathlib import Path
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from material_register.domain.export_dataclass import ExportItemIn, ExportItemOut, PeriodItemIn
from material_register.services.export.period_report import PeriodReport
from material_register.ui.helpers.formating_utils import format_date_range_to_locale


# noinspection PyDunderSlots
class PeriodSheet:
    START_ROW = 1
    LAST_COLUMN = 8

    TITLE_FONT_SIZE = 12
    DEFAULT_FONT_SIZE = 10

    TITLE_ROW_HEIGHT = 20
    DEFAULT_ROW_HEIGHT = 15

    NOTES_ROWS = 4

    ERROR_TEXT = "[N/A]"

    @staticmethod
    def create_sheet(sheet: Worksheet, export_settings: dict[str, Path | str | float | bool],
                     export_texts: dict[str, str],
                     data_in: list[ExportItemIn], out_data: list[ExportItemOut]) -> Worksheet:
        period_in_data = PeriodReport.get_period_data_in(data_in)
        period_out_data = PeriodReport.get_period_data_out(out_data)
        print("period_out_data: ", period_out_data)
        row = PeriodSheet.START_ROW
        row = PeriodSheet._create_header(sheet, row, PeriodSheet.LAST_COLUMN, export_settings, export_texts)
        row, balance = PeriodSheet._create_financial_section(sheet, row, PeriodSheet.LAST_COLUMN, export_settings,
                                                    export_texts)
        row = PeriodSheet._create_data_in_section(sheet, row, PeriodSheet.LAST_COLUMN, export_texts, period_in_data)
        print("final balance: ", balance)
        PeriodSheet._auto_size_columns(sheet)
        sheet.freeze_panes = f"A{row}"
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
        row += 1
        range_text = export_texts.get("rangeText", PeriodSheet.ERROR_TEXT)
        cell = sheet.cell(row, column=1, value=range_text)
        PeriodSheet._cell_alignment(cell, horizontal="left")
        PeriodSheet._cell_font(cell, PeriodSheet.DEFAULT_FONT_SIZE, bold=True)
        period_value = PeriodSheet._get_period_range(export_settings.get("from_date", None),
                                                     export_settings.get("to_date", None))
        cell = sheet.cell(row, column=2, value=period_value)
        sheet.merge_cells(start_row=row, start_column=2, end_row=row, end_column=last_column // 2)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, PeriodSheet.DEFAULT_FONT_SIZE, bold=True)
        branch_text = export_texts.get("branchText", PeriodSheet.ERROR_TEXT)
        cell = sheet.cell(row, column=(last_column // 2) + 1, value=branch_text)
        PeriodSheet._cell_alignment(cell, horizontal="left")
        PeriodSheet._cell_font(cell, PeriodSheet.DEFAULT_FONT_SIZE, bold=True)
        branch_value = export_settings.get("branchNameLineEdit", PeriodSheet.ERROR_TEXT)
        cell = sheet.cell(row, column=(last_column // 2) + 2, value=branch_value)
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 2, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, PeriodSheet.DEFAULT_FONT_SIZE, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        row += 1
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_column)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        return row + 1

    @staticmethod
    def _create_financial_section(sheet: Worksheet, row: int, last_column: int,
                                  export_settings: dict[str, Path | str | float | bool],
                                  export_texts: dict[str, str]) -> tuple[int, float]:
        currency_suffix = export_texts.get("currencySuffix", PeriodSheet.ERROR_TEXT)
        cell_format = f'#,##0.0 "{currency_suffix}";[Red]#,##0.0 "{currency_suffix}"'
        cell = sheet.cell(row=row, column=1, value=export_texts.get("notesText", PeriodSheet.ERROR_TEXT))
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_column // 2)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        cell = sheet.cell(row=row, column=(last_column // 2) + 1, value=export_texts.get("financialText", PeriodSheet.ERROR_TEXT))
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 1, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        row += 1
        cell = sheet.cell(row=row, column=1)
        sheet.merge_cells(start_row=row, start_column=1, end_row=row + PeriodSheet.NOTES_ROWS, end_column=last_column // 2)
        PeriodSheet._cell_alignment(cell, horizontal="left", vertical="top")
        PeriodSheet._cell_font(cell, PeriodSheet.DEFAULT_FONT_SIZE)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        for current_row in range(row, row + PeriodSheet.NOTES_ROWS):
            sheet.row_dimensions[current_row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        opening_balance_row = row
        opening_balance = export_settings.get("openingBalanceSpinbox", 0.0)
        cell = sheet.cell(row=row, column=(last_column // 2) + 1, value=export_texts.get("openingBalanceText", PeriodSheet.ERROR_TEXT))
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 1, end_row=row, end_column=(last_column // 2) + 2)
        PeriodSheet._cell_alignment(cell, horizontal="left")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        cell = sheet.cell(row=row, column=(last_column // 2) + 3, value=opening_balance)
        cell.number_format = cell_format
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 3, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell, horizontal="right")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        row += 1
        income = export_settings.get("income", 0.0)
        cell = sheet.cell(row=row, column=(last_column // 2) + 1, value=export_texts.get("incomeText", PeriodSheet.ERROR_TEXT))
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 1, end_row=row,
                          end_column=(last_column // 2) + 2)
        PeriodSheet._cell_alignment(cell, horizontal="left")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        cell = sheet.cell(row=row, column=(last_column // 2) + 3, value=income)
        cell.number_format = cell_format
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 3, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell, horizontal="right")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        row += 1
        buyback = 99.9 * -1
        cell = sheet.cell(row=row, column=(last_column // 2) + 1, value=export_texts.get("buybackText", PeriodSheet.ERROR_TEXT))
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 1, end_row=row,
                          end_column=(last_column // 2) + 2)
        PeriodSheet._cell_alignment(cell, horizontal="left")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        cell = sheet.cell(row=row, column=(last_column // 2) + 3, value=buyback)
        cell.number_format = cell_format
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 3, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell, horizontal="right")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        row += 1
        expense_row = row
        expense = export_settings.get("expense", 0.0) * -1
        cell = sheet.cell(row=row, column=(last_column // 2) + 1, value=export_texts.get("expenseText", PeriodSheet.ERROR_TEXT))
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 1, end_row=row,
                          end_column=(last_column // 2) + 2)
        PeriodSheet._cell_alignment(cell, horizontal="left")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        cell = sheet.cell(row=row, column=(last_column // 2) + 3, value=expense)
        cell.number_format = cell_format
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 3, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell, horizontal="right")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        row += 1
        cell = sheet.cell(row=row, column=(last_column // 2) + 1, value=export_texts.get("balanceText", PeriodSheet.ERROR_TEXT))
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 1, end_row=row,
                          end_column=(last_column // 2) + 2)
        PeriodSheet._cell_alignment(cell, horizontal="left")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        cell = sheet.cell(row=row, column=(last_column // 2) + 3)
        column_letter = get_column_letter((last_column // 2) + 3)
        balance_value = (
            f"=SUM({column_letter}{opening_balance_row}:{column_letter}{expense_row})"
        )
        cell.value = balance_value
        cell.number_format = cell_format
        sheet.merge_cells(start_row=row, start_column=(last_column // 2) + 3, end_row=row, end_column=last_column)
        PeriodSheet._cell_alignment(cell, horizontal="right")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        row += 1
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_column)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        return row + 1, PeriodSheet._get_balance_value(opening_balance, income, buyback, expense)

    @staticmethod
    def _create_data_in_section(sheet: Worksheet, row: int, last_column: int, export_texts: dict[str, str],
                                in_data: dict[str, list[PeriodItemIn]]) -> int:
        currency_suffix = export_texts.get("currencySuffix", PeriodSheet.ERROR_TEXT)
        money_cell_format = f'#,##0.0 "{currency_suffix}";[Red]#,##0.0 "{currency_suffix}"'
        cell = sheet.cell(row=row, column=1, value=export_texts.get("buybackText", PeriodSheet.ERROR_TEXT))
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_column // 2)
        PeriodSheet._cell_alignment(cell)
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        row += 1
        for category, in_data in in_data.items():
            first_column = 1
            cell = sheet.cell(row=row, column=1, value=category)
            sheet.merge_cells(start_row=row, start_column=first_column, end_row=row, end_column=last_column // 2)
            PeriodSheet._cell_alignment(cell)
            PeriodSheet._cell_font(cell, bold=True)
            sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
            row += 1
            cell = sheet.cell(row=row, column=first_column, value=export_texts.get("commodityText", PeriodSheet.ERROR_TEXT))
            PeriodSheet._cell_alignment(cell)
            PeriodSheet._cell_font(cell, bold=True)
            sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
            cell = sheet.cell(row=row, column=first_column + 1, value=export_texts.get("pricePerUnitText", PeriodSheet.ERROR_TEXT))
            PeriodSheet._cell_alignment(cell)
            PeriodSheet._cell_font(cell, bold=True)
            sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
            cell = sheet.cell(row=row, column=first_column + 2, value=export_texts.get("quantityText", PeriodSheet.ERROR_TEXT))
            PeriodSheet._cell_alignment(cell)
            PeriodSheet._cell_font(cell, bold=True)
            sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
            cell = sheet.cell(row=row, column=first_column + 3, value=export_texts.get("totalPriceText", PeriodSheet.ERROR_TEXT))
            PeriodSheet._cell_alignment(cell)
            PeriodSheet._cell_font(cell, bold=True)
            sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
            row += 1
            row = PeriodSheet._create_category_in_section(sheet, row, last_column, export_texts, in_data, money_cell_format)
        return row + 1

    @staticmethod
    def _create_category_in_section(sheet: Worksheet, row: int, last_column: int, export_texts: dict[str, str],
                                    in_data: list[PeriodItemIn], money_cell_format: str) -> int:
        opening_row = row
        first_column = 1
        for item in in_data:
            quantity_cell_format = f'#,##0.0 "{item.commodity_unit}";[Red]#,##0.0 "{item.commodity_unit}"'
            cell = sheet.cell(row=row, column=first_column, value=item.commodity_name)
            PeriodSheet._cell_alignment(cell)
            PeriodSheet._cell_font(cell, bold=True)
            sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
            cell = sheet.cell(row=row, column=first_column + 1, value=item.price_per_unit)
            cell.number_format = money_cell_format
            PeriodSheet._cell_alignment(cell, horizontal="right")
            PeriodSheet._cell_font(cell)
            sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
            cell = sheet.cell(row=row, column=first_column + 2, value=item.total_quantity)
            cell.number_format = quantity_cell_format
            PeriodSheet._cell_alignment(cell, horizontal="right")
            PeriodSheet._cell_font(cell)
            sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
            cell = sheet.cell(row=row, column=first_column + 3, value=item.total_price)
            cell.number_format = money_cell_format
            PeriodSheet._cell_alignment(cell, horizontal="right")
            PeriodSheet._cell_font(cell, bold=True)
            sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
            row += 1
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=(last_column // 2) - 2)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        cell = sheet.cell(row=row, column=(last_column // 2) - 1, value=export_texts.get("summaryPriceText", PeriodSheet.ERROR_TEXT))
        PeriodSheet._cell_alignment(cell, horizontal="right")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        total_column = get_column_letter(first_column + 3)
        total_value = (
            f"=SUM({total_column}{opening_row}:{total_column}{row -1})"
        )
        cell = sheet.cell(row=row, column=last_column // 2, value=total_value)
        cell.number_format = money_cell_format
        PeriodSheet._cell_alignment(cell, horizontal="right")
        PeriodSheet._cell_font(cell, bold=True)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        row += 1
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_column // 2)
        sheet.row_dimensions[row].height = PeriodSheet.DEFAULT_ROW_HEIGHT
        return row + 1

    @staticmethod
    def _cell_alignment(cell, horizontal: str = "center", vertical: str = "center") -> None:
        cell.alignment = Alignment(horizontal=horizontal, vertical=vertical, wrap_text=True)

    @staticmethod
    def _cell_font(cell, font_size: int | None = None, bold: bool = False) -> None:
        if font_size is None:
            font_size = PeriodSheet.DEFAULT_FONT_SIZE
        cell.font = Font(size=font_size, bold=bold)

    @staticmethod
    def _auto_size_columns(sheet: Worksheet) -> None:
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = get_column_letter(column_cells[0].column)
            for cell in column_cells:
                if cell.value is not None:
                    length = len(str(cell.value))
                    if length > max_length:
                        max_length = length
            sheet.column_dimensions[column_letter].width = max_length + 3

    @staticmethod
    def _get_period_range(from_date: str | None, to_date: str | None) -> str:
        if from_date is None or to_date is None:
            return PeriodSheet.ERROR_TEXT
        return format_date_range_to_locale(from_date, to_date)

    @staticmethod
    def _get_balance_value(opening_balance: float, income: float, buyback: float, expense: float) -> float:
        return round(opening_balance + income + buyback + expense, 1)