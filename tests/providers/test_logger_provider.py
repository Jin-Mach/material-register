from pathlib import Path

from material_register.config.logging_config import LOG_STRUCTURE
from material_register.providers.logger_provider import LoggerProvider


def test_init_loggers(tmp_path: Path) -> None:
    assert LoggerProvider.init_loggers(tmp_path, LOG_STRUCTURE)
    LoggerProvider.ui.error("error message")
    log_file = tmp_path / "ui_logs" / "ui.log"
    assert log_file.exists()
    assert "error message" in log_file.read_text(encoding="utf-8")
