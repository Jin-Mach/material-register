from pathlib import Path

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.database_setup import DatabaseSetup
from material_register.db.migration.database_migration import DatabaseMigration
from material_register.db.utils.database_validator import is_schema_valid
from material_register.services.database_backup_service import DatabaseBackupService
from material_register.services.error_handler import ErrorHandler


def create_connection(
    database_path: Path | None, db_name: str, connection_name: str
) -> QSqlDatabase | None:
    if database_path is None:
        ErrorHandler.handle_error("Database path is None", "db", "critical")
        return None
    connection = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    connection.setDatabaseName(str(database_path / db_name))
    if not connection.open():
        ErrorHandler.handle_error(connection.lastError().text(), "db", "critical")
        return None
    if not DatabaseSetup.setup_init(connection):
        connection.close()
        return None
    is_new, error = DatabaseSetup.is_new_database(connection)
    if error:
        ErrorHandler.handle_error(error, "db", "critical")
        connection.close()
        return None
    if not is_new and not DatabaseMigration.migration_init(connection):
        ErrorHandler.handle_error(connection.lastError().text(), "db", "critical")
        connection.close()
        return None
    migration_completed = False
    if not is_new:
        current_version = DatabaseMigration.DB_VERSION
        latest_version = max(DatabaseMigration.MIGRATIONS_MAP)
        if current_version < latest_version:
            database_file = database_path / db_name
            history_directory = database_path / "history"
            history_directory.mkdir(parents=True, exist_ok=True)
            backup_path = (
                history_directory / f"{database_file.stem}_V{current_version}.db"
            )
            if (
                not backup_path.exists()
                and not DatabaseBackupService.create_custom_backup(
                    database_file, backup_path
                )
            ):
                connection.close()
                return None
            if not DatabaseMigration.migrate(connection):
                connection.close()
                return None
            migration_completed = True
    result, last_query = create_db_tables(connection)
    if not result:
        ErrorHandler.handle_error(last_query.lastError().text(), "db", "critical")
        connection.close()
        return None
    ok, error = is_schema_valid(connection)
    if not ok:
        ErrorHandler.handle_error(error, "db", "critical")
        connection.close()
        return None
    if migration_completed:
        if not DatabaseBackupService.delete_backup_folder():
            connection.close()
            return None
    return connection


def create_db_tables(connection: QSqlDatabase) -> tuple[bool, QSqlQuery]:
    query = QSqlQuery(connection)

    if not query.exec("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            first_name TEXT,
            last_name TEXT,
            document_number TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1,
            company_normalized TEXT,
            first_name_normalized TEXT,
            last_name_normalized TEXT,
            address_normalized TEXT,
            
            CHECK(company IS NULL OR company <> ''),
            CHECK(first_name IS NULL OR first_name <> ''),
            CHECK(last_name IS NULL OR last_name <> ''),
            CHECK(document_number <> ''),
            CHECK(address <> ''),
        
            CHECK (
                (company IS NOT NULL AND first_name IS NULL AND last_name IS NULL)
                OR
                (company IS NULL AND first_name IS NOT NULL AND last_name IS NOT NULL)
            )
        )
    """):
        return False, query

    if not query.exec("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            notes TEXT,
        
            CHECK(name <> '')
        )
    """):
        return False, query

    if not query.exec("""
        CREATE TABLE IF NOT EXISTS commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category_id INTEGER,
            unit TEXT DEFAULT 'kg',
            default_price REAL DEFAULT 0,
            notes TEXT,
            active INTEGER DEFAULT 1,
        
            CHECK(name <> ''),
        
            FOREIGN KEY(category_id)
                REFERENCES categories(id)
                ON DELETE RESTRICT
)
    """):
        return False, query

    if not query.exec("""
        CREATE TABLE IF NOT EXISTS inventory (
            commodity_id INTEGER PRIMARY KEY,
            stock REAL NOT NULL DEFAULT 0,

            FOREIGN KEY(commodity_id)
                REFERENCES commodities(id)
                ON DELETE RESTRICT
        )
    """):
        return False, query

    if not query.exec("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            customer_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            payment_type TEXT,
            is_invoiced INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            
            CHECK(type IN ('IN', 'OUT')),
            CHECK (
                (type = 'IN' AND payment_type IN ('CASH', 'TRANSFER')) 
                OR 
                (type = 'OUT' AND payment_type IS NULL)
            ),
            CHECK(is_invoiced IN (0, 1)),

            FOREIGN KEY(customer_id)
                REFERENCES customers(id)
                ON DELETE SET NULL
        )
    """):
        return False, query

    if not query.exec("""
        CREATE TABLE IF NOT EXISTS transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            commodity_id INTEGER NOT NULL,
            unit_count REAL NOT NULL,
            price_per_unit REAL NOT NULL,
            
            CHECK(unit_count > 0),
            CHECK(price_per_unit >= 0),

            FOREIGN KEY(transaction_id)
                REFERENCES transactions(id)
                ON DELETE CASCADE,

            FOREIGN KEY(commodity_id)
                REFERENCES commodities(id)
                ON DELETE RESTRICT
        )
    """):
        return False, query

    if not query.exec("""
        CREATE TRIGGER IF NOT EXISTS trigger_new_commodity
        AFTER INSERT ON commodities
        BEGIN
            INSERT INTO inventory (commodity_id, stock)
            VALUES (NEW.id, 0);
        END
    """):
        return False, query

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_commodities_category ON commodities(category_id)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_items_transaction ON transaction_items(transaction_id)",
    ]

    for sql in indexes:
        if not query.exec(sql):
            return False, query

    return True, query
