from pathlib import Path

from material_register.providers.settings_provider import SettingsProvider


def _create_settings_file(tmp_path: Path, data: str) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    file = config_dir / "settings.toml"
    file.write_text(data, encoding="utf-8")


def test_save_settings(tmp_path: Path) -> None:
    data = """
            [export.default]
            branchNameLineEdit = "Some branch"
            pathLineEdit = "/tmp/export"
            saveLastBalanceCheckbox = true
            openingBalanceSpinbox = 1000.0
            """
    _create_settings_file(tmp_path, data)
    SettingsProvider.provider_init(tmp_path)
    SettingsProvider.SETTINGS["export"]["default"]["branchNameLineEdit"] = (
        "Updated branch"
    )
    SettingsProvider.SETTINGS["export"]["default"]["openingBalanceSpinbox"] = 2000.0
    result = SettingsProvider.save_settings()
    assert result is True
    SettingsProvider.provider_init(tmp_path)
    assert (
        SettingsProvider.SETTINGS["export"]["default"]["branchNameLineEdit"]
        == "Updated branch"
    )
    assert (
        SettingsProvider.SETTINGS["export"]["default"]["openingBalanceSpinbox"]
        == 2000.0
    )


def test_load_settings_valid(tmp_path: Path) -> None:
    data = """
            [export.default]
            branchNameLineEdit = "Some branch"
            pathLineEdit = "/tmp/export"
            saveLastBalanceCheckbox = true
            openingBalanceSpinbox = 1000.0
            """
    _create_settings_file(tmp_path, data)
    SettingsProvider.provider_init(tmp_path)
    assert (
        SettingsProvider.SETTINGS["export"]["default"]["branchNameLineEdit"]
        == "Some branch"
    )
    assert (
        SettingsProvider.SETTINGS["export"]["default"]["saveLastBalanceCheckbox"]
        is True
    )
    assert (
        SettingsProvider.SETTINGS["export"]["default"]["openingBalanceSpinbox"]
        == 1000.0
    )


def test_load_settings_empty(tmp_path: Path) -> None:
    data = ""
    _create_settings_file(tmp_path, data)
    SettingsProvider.provider_init(tmp_path)
    assert SettingsProvider.SETTINGS == {}


def test_load_settings_missing_path(tmp_path: Path) -> None:
    SettingsProvider.provider_init(tmp_path)
    assert SettingsProvider.SETTINGS == {}
