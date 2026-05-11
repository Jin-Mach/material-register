import json
import pytest

from pathlib import Path

from material_register.config.file_config import UI_KEYS, HEADERS_KEYS
from material_register.providers.file_provider import FileProvider


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

def write_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("img", encoding="utf-8")

def create_valid_ui() -> dict[str, dict[str, str]]:
    data = {}
    for section, key in UI_KEYS:
        data.setdefault(section, {})[key] = "x"
    return data

def create_valid_error() -> dict[str, str]:
    return {
        "APP_INIT_FAILED": "x",
        "RESOURCES_MISSING": "x",
        "DOWNLOAD_FAILED": "x",
        "TEXTS_LOAD_FAILED": "x",
        "CRITICAL_FAILURE": "x",
        "UNKNOWN_ERROR": "x",
    }

def create_valid_headers() -> dict[str, dict[str, str]]:
    data = {}
    for section, key in HEADERS_KEYS:
        data.setdefault(section, {})[key] = "x"
    return data

def create_base_structure(base: Path) -> None:
    ui = create_valid_ui()
    error = create_valid_error()
    headers = create_valid_headers()
    write_json(base / "texts" / "cs_CZ" / "ui_texts.json", ui)
    write_json(base / "texts" / "en_GB" / "ui_texts.json", ui)
    write_json(base / "texts" / "cs_CZ" / "error_texts.json", error)
    write_json(base / "texts" / "en_GB" / "error_texts.json", error)
    write_json(base / "texts" / "cs_CZ" / "headers_texts.json", headers)
    write_json(base / "texts" / "en_GB" / "headers_texts.json", headers)
    write_image(base / "images" / "SplashScreen.jpg")

@pytest.mark.parametrize(
    "modify, expected_missing",
    [
        ("valid", 0),
        ("missing_en", 1),
        ("invalid_en", 1),
    ],
    ids=["all valid", "missing en_GB file", "invalid json"],
)
def test_check_missing_files(tmp_path: Path, modify, expected_missing) -> None:
    base = tmp_path / "resources"
    create_base_structure(base)
    target = base / "texts" / "en_GB" / "ui_texts.json"
    if modify == "missing_en":
        target.unlink()
    if modify == "invalid_en":
        target.write_text("not json", encoding="utf-8")
    result = FileProvider.check_missing_files(base)
    if modify == "valid":
        assert len(result) == 0
    if modify == "missing_en":
        assert any("en_GB" in str(p) for p in result)
        assert len(result) == 1
    if modify == "invalid_en":
        assert any("en_GB" in str(p) for p in result)
        assert len(result) == 1