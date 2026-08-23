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
