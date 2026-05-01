import json
import pytest

from pathlib import Path

from material_register.providers.file_provider import FileProvider


VALID_UI_JSON = {
    "MainWindow": {"titleText": "Title"},
    "SidePanel": {
        "registerButtonText": "A",
        "registerButtonTooltipText": "B",
    },
    "ActionsWidget": {
        "addActionButtonTooltipText": "C",
        "deleteActionButtonTooltipText": "D",
    },
    "ErrorDialog": {
        "closeDialogButtonText": "x",
        "closeDialogButtonTooltipText": "x",
        "closeAppButtonText": "x",
        "closeAppButtonTooltipText": "x",
    },
}

VALID_ERROR_JSON = {
    "APP_INIT_FAILED": "x",
    "RESOURCES_MISSING": "x",
    "DOWNLOAD_FAILED": "x",
    "TEXTS_LOAD_FAILED": "x",
    "CRITICAL_FAILURE": "x",
    "UNKNOWN_ERROR": "x",
    "CONNECTION_ERROR": "x",
    "PERMISSION_ERROR": "x"
}

def write_valid(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "ui_texts.json").write_text(json.dumps(VALID_UI_JSON), encoding="utf-8")
    (path / "error_texts.json").write_text(json.dumps(VALID_ERROR_JSON), encoding="utf-8")

@pytest.fixture
def resources_structure(tmp_path: Path) -> Path:
    base = tmp_path
    write_valid(base / "texts" / "cs_CZ")
    write_valid(base / "texts" / "en_GB")
    write_valid(base / "errors" / "cs_CZ")
    write_valid(base / "errors" / "en_GB")
    return base


@pytest.mark.parametrize(
    "modify, expected_count",[
        ("valid", 0),
        ("missing_en", 1),
        ("invalid_en", 1),
    ],
    ids=["all valid", "missing en_GB file", "invalid json"]
)

def test_check_missing_files(resources_structure: Path, modify, expected_count):
    if modify == "missing_en":
        (resources_structure / "texts" / "en_GB" / "ui_texts.json").unlink()
    elif modify == "invalid_en":
        (resources_structure / "texts" / "en_GB" / "ui_texts.json").write_text("not json", encoding="utf-8")
    result = FileProvider.check_missing_files(resources_structure)
    assert len(result) == expected_count