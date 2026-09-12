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


def is_integrity_valid(connection: QSqlDatabase) -> tuple[bool, str]:
    query = QSqlQuery(connection)
    if not query.exec("PRAGMA integrity_check"):
        return False, f"PRAGMA integrity check failed: {query.lastError().text()}"
    while query.next():
        result = query.value(0)
        if result != "ok":
            return False, result
    return True, ""


def are_foreign_keys_valid(connection: QSqlDatabase) -> tuple[bool, list[str]]:
    errors_list = []
    query = QSqlQuery(connection)
    if not query.exec("PRAGMA foreign_key_check"):
        errors_list.append(
            f"PRAGMA foreign_key_check failed: {query.lastError().text()}"
        )
        return False, errors_list
    while query.next():
        table_name = query.value(0)
        row_id = query.value(1)
        parent_table_name = query.value(2)
        foreign_key_id = query.value(3)
        error = (
            f"Row {row_id} in table {table_name} has an invalid foreign key reference to table {parent_table_name}"
            f"(foreign key {foreign_key_id})"
        )
        errors_list.append(error)
    if errors_list:
        return False, errors_list
    return True, []
