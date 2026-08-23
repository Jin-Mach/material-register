from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.db_constants import DATABASE_SCHEMA


def is_schema_valid(connection: QSqlDatabase) -> tuple[bool, str]:
    for table_name, expected_columns in DATABASE_SCHEMA.items():
        query = QSqlQuery(connection)
        if not query.exec(f"PRAGMA table_info({table_name})"):
            return False, f"Cannot read schema for table: {table_name}"
        columns = set()
        while query.next():
            columns.add(query.value("name"))
        if columns != expected_columns:
            missing = expected_columns - columns
            extra = columns - expected_columns
            return False, (
                f"Schema mismatch in table '{table_name}'. "
                f"Missing: {', '.join(sorted(missing)) or 'none'}. "
                f"Extra: {', '.join(sorted(extra)) or 'none'}."
            )
    return True, ""
