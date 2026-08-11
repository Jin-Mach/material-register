import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session", autouse=True)
def fake_app():
    app = QApplication.instance() or QApplication([])
    yield app
