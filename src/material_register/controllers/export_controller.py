from typing import TYPE_CHECKING

from material_register.db.queries.export_queries import ExportQueries
from material_register.init.db_init import DbInit

if TYPE_CHECKING:
    from material_register.ui.export.export_widget import ExportWidget


class ExportController:
    def __init__(self, export_widget: "ExportWidget") -> None:
        self.export_widget = export_widget
        self.db_connection = DbInit.db_connection
        self.thread = None
        self.worker = None

    def start_export(self) -> None:
        export_settings = self.export_widget.get_export_data()
        in_data = ExportQueries.load_export_data_in(self.db_connection, export_settings["from_date"], export_settings["to_date"])
        out_data = ExportQueries.load_export_data_out(self.db_connection, export_settings["from_date"], export_settings["to_date"])
        print("in_data: ", in_data)
        print("out_data: ", out_data)