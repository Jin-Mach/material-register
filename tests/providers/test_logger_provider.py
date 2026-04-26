from pathlib import Path

from material_register.providers.logger_provider import LoggerProvider


log_structure = {
    "app": ("app_logs", "app.log"),
    "ui": ("ui_logs", "ui.log"),
    "db": ("db_logs", "db.log"),
    "error": ("error_logs", "error.log"),
}

def test_init_loggers(tmp_path: Path) -> None:
    LoggerProvider.init_loggers(tmp_path, log_structure)
    LoggerProvider.ui.error("error message")
    log_file = tmp_path / "ui_logs" / "ui.log"
    assert log_file.exists()
    assert "error message" in log_file.read_text(encoding="utf-8")