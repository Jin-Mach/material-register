from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.worksheet.worksheet import Worksheet


def cell_alignment(cell, horizontal: str = "center", vertical: str = "center") -> None:
    cell.alignment = Alignment(horizontal=horizontal, vertical=vertical, wrap_text=True)


def cell_font(
    cell,
    font_size: int | None = None,
    bold: bool = False,
    default_font_size: int | None = None,
) -> None:
    if font_size is None:
        font_size = default_font_size
    cell.font = Font(size=font_size, bold=bold)


def set_borders(
    sheet: Worksheet,
    start_row: int,
    start_column: int,
    end_row: int,
    end_column: int,
    style: str = "thin",
) -> None:
    side = Side(border_style=style)
    for row in sheet.iter_rows(
        min_row=start_row, max_row=end_row, min_col=start_column, max_col=end_column
    ):
        for cell in row:
            top = None
            bottom = None
            left = None
            right = None
            if cell.row == start_row:
                top = side
            if cell.row == end_row:
                bottom = side
            if cell.column == start_column:
                left = side
            if cell.column == end_column:
                right = side
            cell.border = Border(top=top, bottom=bottom, left=left, right=right)
