import uuid
from pathlib import Path

from PySide6.QtSql import QSqlDatabase


def create_external_connection(
    database_file: Path | None, connection_name: str
) -> tuple[bool, QSqlDatabase | None, str]:
    if database_file is None:
        return False, None, "Database is None"
    connection_name = f"{connection_name}.{uuid.uuid4().hex}"
    connection = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    connection.setDatabaseName(str(database_file))
    connection.setConnectOptions("QSQLITE_OPEN_READONLY")
    if not connection.open():
        error = connection.lastError().text()
        connection.close()
        del connection
        QSqlDatabase.removeDatabase(connection_name)
        return False, None, f"Open connection failed: {error}"
    return True, connection, ""
