import json
from pathlib import Path

import pytest

from material_register.providers.file_provider import FileProvider

FAKE_JSON_FILES = [Path("en_GB") / "ui_texts.json"]
FAKE_IMAGES = [Path("system") / "splash.png"]
FAKE_STYLES = [Path("dark_blue.qss")]
FAKE_UI_KEYS = [("MainWindow", "titleText")]
FAKE_HEADERS_KEYS = [("CustomersView", "company")]
FAKE_NOTIFICATION_KEYS = [("CUSTOMERS", "ADD_CUSTOMER")]


def write_settings(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
        [export.default]
        branchNameLineEdit = ""
        """,
        encoding="utf-8",
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def write_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("img", encoding="utf-8")

def write_style(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("QWidget { color: white; }", encoding="utf-8")

def create_valid_ui() -> dict:
    data = {}
    for section, key in FAKE_UI_KEYS:
        data.setdefault(section, {})[key] = "x"
    return data


def create_valid_error() -> dict:
    return {
        "APP_INIT_FAILED": "x",
        "RESOURCES_MISSING": "x",
        "DOWNLOAD_FAILED": "x",
        "TEXTS_LOAD_FAILED": "x",
        "CRITICAL_FAILURE": "x",
        "UNKNOWN_ERROR": "x",
    }


def create_valid_headers() -> dict:
    data = {}
    for section, key in FAKE_HEADERS_KEYS:
        data.setdefault(section, {})[key] = "x"
    return data


def create_valid_confirm() -> dict:
    return {"UPDATE": {"TITLE": "x", "TEXT": "x", "YES": "x", "NO": "x"}}


def create_valid_notification() -> dict:
    data = {}
    for section, key in FAKE_NOTIFICATION_KEYS:
        data.setdefault(section, {})[key] = "x"
    return data


@pytest.fixture(autouse=True)
def patch_file_config(monkeypatch):
    monkeypatch.setattr(
        "material_register.providers.file_provider.REQUIRED_JSON_FILES", FAKE_JSON_FILES
    )
    monkeypatch.setattr(
        "material_register.providers.file_provider.REQUIRED_IMAGES", FAKE_IMAGES
    )
    monkeypatch.setattr(
        "material_register.providers.file_provider.REQUIRED_STYLES_FILES",
        FAKE_STYLES,
    )
    monkeypatch.setattr(
        "material_register.providers.file_provider.UI_KEYS", FAKE_UI_KEYS
    )
    monkeypatch.setattr(
        "material_register.providers.file_provider.HEADERS_KEYS", FAKE_HEADERS_KEYS
    )
    monkeypatch.setattr(
        "material_register.providers.file_provider.NOTIFICATION_KEYS",
        FAKE_NOTIFICATION_KEYS,
    )


def test_check_missing_files(tmp_path: Path) -> None:
    base = tmp_path / "resources"
    write_json(base / "texts" / "en_GB" / "ui_texts.json", create_valid_ui())
    write_image(base / "images" / "system" / "splash.png")
    write_settings(base / "config" / "settings.toml")
    write_style(base / "dark_blue.qss")
    result = FileProvider.check_missing_files(base)
    assert len(result) == 0

def test_check_missing_files_reports_missing(tmp_path: Path) -> None:
    base = tmp_path / "resources"
    result = FileProvider.check_missing_files(base)
    assert len(result) == 4
