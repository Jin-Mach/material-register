import pytest

from material_register.services.error_handler import ErrorHandler


class FakeLogger:
    def __init__(self):
        self.calls = []

    def warning(self, msg, exc_info=None):
        self.calls.append(("warning", msg, exc_info))

    def error(self, msg, exc_info=None):
        self.calls.append(("error", msg, exc_info))

    def critical(self, msg, exc_info=None):
        self.calls.append(("critical", msg, exc_info))

@pytest.fixture
def fake_logger():
    return FakeLogger()

@pytest.mark.parametrize(
    "level, expected",
    [
        ("warning", ("warning", "fail", None)),
        ("error", ("error", "fail", None)),
        ("critical", ("critical", "fail", None)),
        ("invalid", ("warning", "fail", None)),
    ],
)
def test_handle_error(level, expected, fake_logger):
    ErrorHandler.loggers_map = {"app": fake_logger}
    ErrorHandler.handle_error("fail", "app", level)
    assert fake_logger.calls[0] == expected

def test_handle_error_exception(fake_logger):
    ErrorHandler.loggers_map = {"app": fake_logger}
    ErrorHandler.handle_error(ValueError("fail"), "app", "error")
    assert fake_logger.calls[0][0] == "error"
    assert fake_logger.calls[0][1] is not None
    assert fake_logger.calls[0][2] is True