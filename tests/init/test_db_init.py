from material_register.init import db_init

FAKE_CONNECTION = object()


def fake_create_connection_failed(base, name, conn_name):
    return None


def fake_create_connection_success(base, name, conn_name):
    return FAKE_CONNECTION


def fake_is_schema_valid(connection):
    return True, ""


def test_init_db_create_connection_failed(monkeypatch):
    monkeypatch.setattr(db_init, "create_connection", fake_create_connection_failed)
    result = db_init.DbInit.init_db()
    assert result == (False, "DATABASE_FAILED")


def test_init_db_success_sets_db_connection(monkeypatch):
    monkeypatch.setattr(db_init, "create_connection", fake_create_connection_success)
    monkeypatch.setattr(db_init, "is_schema_valid", fake_is_schema_valid)
    db_init.DbInit.db_connection = None
    result = db_init.DbInit.init_db()
    assert result == (True, "")
    assert db_init.DbInit.db_connection is FAKE_CONNECTION
