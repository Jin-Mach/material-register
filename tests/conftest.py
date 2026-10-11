from collections.abc import Generator

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session", autouse=True)
def fake_app() -> Generator[QApplication]:
    app = QApplication.instance() or QApplication([])
    yield app
