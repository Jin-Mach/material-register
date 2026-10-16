from material_register.init import data_init
from material_register.ui.config.ui_constants import LOG_LEVEL_CRITICAL, LOGGER_DB


def test_init_data_propagates_cache_setup_failure(monkeypatch) -> None:
    monkeypatch.setattr(data_init.DbInit, "db_connection", object())
    monkeypatch.setattr(data_init, "CustomersModel", lambda connection: object())
    monkeypatch.setattr(
        data_init.DbCache,
        "setup_init",
        lambda self: (False, "customer query failed"),
    )
    errors = []
    monkeypatch.setattr(
        data_init.ErrorHandler,
        "handle_error",
        lambda message, logger, level: errors.append((message, logger, level)),
    )
    result = data_init.DataInit.init_data()
    assert result == (False, "DATABASE_FAILED")
    assert errors == [("customer query failed", LOGGER_DB, LOG_LEVEL_CRITICAL)]
