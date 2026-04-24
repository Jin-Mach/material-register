import json
import pytest

from pathlib import Path

from material_register.providers.file_provider import FileProvider


VALID_JSON = {
    "MainWindow": {"titleText": "Title"},
    "SidePanel": {
        "registerButtonText": "A",
        "registerButtonTooltipText": "B"
    },
    "ActionsWidget": {
        "addActionButtonTooltipText": "C",
        "deleteActionButtonTooltipText": "D"
    }
}

def write_valid(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "ui_texts.json").write_text(json.dumps(VALID_JSON), encoding="utf-8")

@pytest.fixture
def texts_structure(tmp_path: Path) -> Path:
    base = tmp_path / "texts"
    write_valid(base / "cs_CZ")
    write_valid(base / "en_GB")
    return base

@pytest.mark.parametrize(
    "modify, expected_count",[
        ("valid", 0),
        ("missing_en", 1),
        ("invalid_en", 1),
    ],
    ids=["all valid", "missing en_GB file", "invalid json"]
)
def test_check_texts_files(texts_structure: Path, modify, expected_count):
    if modify == "missing_en":
        (texts_structure / "en_GB" / "ui_texts.json").unlink()
    elif modify == "invalid_en":
        (texts_structure / "en_GB" / "ui_texts.json").write_text("not json")
    result = FileProvider._check_texts_files(texts_structure)
    assert len(result) == expected_count