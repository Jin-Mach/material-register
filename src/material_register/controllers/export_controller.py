from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from material_register.ui.export.export_widget import ExportWidget


class ExportController:
    def __init__(self, export_widget: "ExportWidget") -> None:
        self.export_widget = export_widget
        self.thread = None
        self.worker = None

    def start_export(self) -> None:
        export_settings = self.export_widget.get_export_data()
        print("export settings:", export_settings)