from openpyxl import Workbook

from material_register.domain.export_dataclass import ExportItemIn, ExportItemOut
from material_register.services.export.excel.period.period_sheet import PeriodSheet


class PeriodWorkbook:

    @staticmethod
    def create_workbook(in_data: list[ExportItemIn], out_data: list[ExportItemOut]) -> Workbook:
        workbook = Workbook()
        workbook.remove(workbook.active)
        sheet = workbook.create_sheet("test")
        PeriodSheet.create_sheet(sheet, in_data, out_data)
        return workbook