from pathlib import Path

from material_register.providers.settings_provider import SettingsProvider


def _create_settings_file(file_path: Path, data: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(data, encoding="utf-8")


def test_save_settings(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    data = """
    [export.summary.default]
    branchNameLineEdit = "Some branch"
    openingBalanceSpinbox = 1000.0
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    SettingsProvider.SETTINGS["export"]["summary"]["default"]["branchNameLineEdit"] = (
        "Updated branch"
    )
    SettingsProvider.SETTINGS["export"]["summary"]["default"][
        "openingBalanceSpinbox"
    ] = 2000.0
    result = SettingsProvider.save_settings()
    assert result is True
    user_settings = SettingsProvider._load_settings(config_path / "settings.toml")
    assert (
        user_settings["export"]["summary"]["default"]["branchNameLineEdit"]
        == "Updated branch"
    )
    assert (
        user_settings["export"]["summary"]["default"]["openingBalanceSpinbox"] == 2000.0
    )


def test_restore_settings(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    data = """
    [export.summary.default]
    branchNameLineEdit = "Default branch"
    pathLineEdit = "/default/path"

    [export.summary.user]
    branchNameLineEdit = "User branch"
    pathLineEdit = "/user/path"
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    result = SettingsProvider.restore_settings("export", "summary")
    assert result is True
    settings = SettingsProvider.SETTINGS["export"]["summary"]["user"]
    assert settings["branchNameLineEdit"] == "Default branch"
    assert settings["pathLineEdit"] == "/default/path"


def test_load_settings_valid(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    data = """
    [export.summary.default]
    branchNameLineEdit = "Some branch"
    pathLineEdit = "/tmp/export"
    saveLastBalanceCheckbox = true
    openingBalanceSpinbox = 1000.0
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        data,
    )
    SettingsProvider.provider_init(resources_path, tmp_path / "config")
    assert (
        SettingsProvider.SETTINGS["export"]["summary"]["default"]["branchNameLineEdit"]
        == "Some branch"
    )
    assert (
        SettingsProvider.SETTINGS["export"]["summary"]["default"][
            "saveLastBalanceCheckbox"
        ]
        is True
    )
    assert (
        SettingsProvider.SETTINGS["export"]["summary"]["default"][
            "openingBalanceSpinbox"
        ]
        == 1000.0
    )


def test_load_settings_empty(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        "",
    )
    SettingsProvider.provider_init(resources_path, tmp_path / "config")
    assert SettingsProvider.SETTINGS == {}


def test_load_settings_missing_path(tmp_path: Path) -> None:
    SettingsProvider.provider_init(
        tmp_path / "resources",
        tmp_path / "config",
    )
    assert SettingsProvider.SETTINGS == {}


def test_update_settings_creates_user_settings(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    data = """
    [export.summary.default]
    branchNameLineEdit = "Some branch"
    openingBalanceSpinbox = 1000.0
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    result = SettingsProvider.update_settings()
    assert result is True
    assert (
        SettingsProvider.SETTINGS["export"]["summary"]["default"]["branchNameLineEdit"]
        == "Some branch"
    )
    assert (config_path / "settings.toml").exists()


def test_update_settings_updates_keys(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    default_data = """
    [export.summary.default]
    branchNameLineEdit = "Default branch"
    pathLineEdit = "/default/path"
    newSetting = true

    [export.summary.user]
    branchNameLineEdit = "Default branch"
    pathLineEdit = "/default/path"
    newSetting = true
    """
    user_data = """
    [export.summary.default]
    branchNameLineEdit = "Default branch"
    pathLineEdit = "/default/path"
    removedSetting = true

    [export.summary.user]
    branchNameLineEdit = "User branch"
    pathLineEdit = "/user/path"
    removedSetting = true
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        default_data,
    )
    _create_settings_file(
        config_path / "settings.toml",
        user_data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    result = SettingsProvider.update_settings()
    assert result is True
    settings = SettingsProvider.SETTINGS["export"]["summary"]
    assert settings["default"]["branchNameLineEdit"] == "Default branch"
    assert settings["default"]["pathLineEdit"] == "/default/path"
    assert settings["default"]["newSetting"] is True
    assert "removedSetting" not in settings["default"]
    assert settings["user"]["branchNameLineEdit"] == "User branch"
    assert settings["user"]["pathLineEdit"] == "/user/path"
    assert settings["user"]["newSetting"] is True
    assert "removedSetting" not in settings["user"]


def test_update_settings_sections(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    data = """
    [export.summary.default]
    branchNameLineEdit = "Default branch"
    pathLineEdit = "/default/path"
    newSetting = true

    [export.summary.user]
    branchNameLineEdit = "User branch"
    pathLineEdit = "/user/path"
    removedSetting = true
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    SettingsProvider.update_settings_sections(
        "export",
        "summary",
        ["branchNameLineEdit", "pathLineEdit", "newSetting"],
    )
    settings = SettingsProvider.SETTINGS["export"]["summary"]
    assert settings["default"]["branchNameLineEdit"] == "Default branch"
    assert settings["default"]["pathLineEdit"] == "/default/path"
    assert settings["default"]["newSetting"] is True
    assert settings["user"]["branchNameLineEdit"] == "User branch"
    assert settings["user"]["pathLineEdit"] == "/user/path"
    assert settings["user"]["newSetting"] == 0
    assert "removedSetting" not in settings["user"]


def test_update_settings_cash_balance_values(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    default_data = """
    [tools.cash_balance_values.default]
    [tools.cash_balance_values.user]
    """
    user_data = """
    [tools.cash_balance_values.default]
    5000 = 0
    2000 = 0
    [tools.cash_balance_values.user]
    5000 = 10
    2000 = 5
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        default_data,
    )
    _create_settings_file(
        config_path / "settings.toml",
        user_data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    result = SettingsProvider.update_settings()
    assert result is True
    cash = SettingsProvider.SETTINGS["tools"]["cash_balance_values"]
    assert cash["user"]["5000"] == 10
    assert cash["user"]["2000"] == 5


def test_restore_settings_missing_user(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    data = """
    [export.summary.default]
    branchNameLineEdit = "Default branch"
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    result = SettingsProvider.restore_settings("export", "summary")
    assert result is False


def test_restore_settings_missing_default(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    data = """
    [export.summary.user]
    branchNameLineEdit = "User branch"
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    result = SettingsProvider.restore_settings("export", "summary")
    assert result is False


def test_restore_settings_missing_user_key(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    data = """
    [export.summary.default]
    branchNameLineEdit = "Default branch"
    pathLineEdit = "/default/path"

    [export.summary.user]
    branchNameLineEdit = "User branch"
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    result = SettingsProvider.restore_settings("export", "summary")
    assert result is True
    settings = SettingsProvider.SETTINGS["export"]["summary"]["user"]
    assert settings["branchNameLineEdit"] == "Default branch"
    assert "pathLineEdit" not in settings


def test_load_settings_invalid(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    settings_path = resources_path / "config" / "settings.toml"
    _create_settings_file(
        settings_path,
        "[invalid",
    )
    SettingsProvider.provider_init(resources_path, tmp_path / "config")
    assert SettingsProvider.SETTINGS == {}


def test_update_settings_sections_default_value(tmp_path: Path) -> None:
    resources_path = tmp_path / "resources"
    config_path = tmp_path / "config"
    data = """
    [export.summary.default]
    branchNameLineEdit = "Default branch"

    [export.summary.user]
    branchNameLineEdit = "User branch"
    """
    _create_settings_file(
        resources_path / "config" / "settings.toml",
        data,
    )
    SettingsProvider.provider_init(resources_path, config_path)
    SettingsProvider.update_settings_sections(
        "export",
        "summary",
        ["branchNameLineEdit", "newSetting"],
        default_value=5,
    )
    settings = SettingsProvider.SETTINGS["export"]["summary"]
    assert settings["default"]["newSetting"] == 5
    assert settings["user"]["newSetting"] == 5
