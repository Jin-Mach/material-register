from collections.abc import Generator

import pytest
from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session", autouse=True)
def fake_app() -> Generator[QApplication]:
    app = QApplication.instance() or QApplication([])
    yield app


def pytest_sessionfinish(session, exitstatus) -> None:
    for name in QSqlDatabase.connectionNames():
        if name.startswith("test_"):
            db = QSqlDatabase.database(name, open=False)
            db.close()
            del db
            QSqlDatabase.removeDatabase(name)
