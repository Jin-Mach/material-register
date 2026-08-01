from openpyxl import Workbook

from material_register.domain.export_dataclass import ExportItemIn, ExportItemOut


class PeriodWorkbook:

    @staticmethod
    def create_workbook(in_data: list[ExportItemIn], out_data: list[ExportItemOut]) -> Workbook:
        workbook = Workbook()
        #workbook.remove(workbook.active)
        print("in data:", in_data)
        print("out data:", out_data)
        return workbook