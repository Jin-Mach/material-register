from PySide6.QtCore import QObject, Signal, Slot

from material_register.init.app_init import AppInit
from material_register.init.db_init import DbInit
from material_register.init.data_init import DataInit
from material_register.init.setup_init import SetupInit


class InitWorker(QObject):
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()

    @Slot()
    def run(self) -> None:
        app_ok, app_error = AppInit.init_app()
        if not app_ok:
            self.error_signal.emit(app_error)
            return
        setup_ok, setup_error = SetupInit.init_setup()
        if not setup_ok:
            self.error_signal.emit(setup_error)
            return
        db_ok, db_error = DbInit.init_db()
        if not db_ok:
            self.error_signal.emit(db_error)
            return
        models_ok, models_error = DataInit.init_data()
        if not models_ok:
            self.error_signal.emit(models_error)
            return
        self.finished_signal.emit()