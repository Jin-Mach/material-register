import pytest

from material_register.services.error_handler import ErrorHandler

calls = []

def _warning(message: str) -> None:
    calls.append(("warning", message))

def _error(message: str) -> None:
    calls.append(("error", message))

def _critical(message: str) -> None:
    calls.append(("critical", message))

fake_logger = {
    "warning": _warning,
    "error": _error,
    "critical": _critical
}

@pytest.mark.parametrize("level, expected", [
        ("warning", ("warning", "fail")),
        ("error", ("error", "fail")),
        ("critical", ("critical", "fail")),
        ("invalid", ("warning", "fail")),
        ]
)
def test_handle_error(level, expected) -> None:
    calls.clear()
    ErrorHandler.loggers_map = {"app": fake_logger}
    ErrorHandler.handle_error("fail", "app", level)
    assert calls[0] == expected
