import json

from pathlib import Path

from material_register.providers.texts_provider import TextsProvider

def _create_texts_file(tmp_path: Path, language: str, data: dict) -> None:
    lang_dir = tmp_path / "texts" / language
    lang_dir.mkdir(parents=True, exist_ok=True)
    file = lang_dir / "ui_texts.json"
    file.write_text(json.dumps(data), encoding="utf-8")

def test_load_ui_texts_valid(tmp_path: Path) -> None:
    language = "en_GB"
    data = {"MainWindow": {"title": "Window Title"}}
    _create_texts_file(tmp_path, language, data)
    TextsProvider.provider_init(language, tmp_path)
    assert TextsProvider.UI_TEXTS["MainWindow"]["title"] == "Window Title"

def test_load_ui_texts_empty(tmp_path: Path) -> None:
    language = "en_GB"
    data = {}
    _create_texts_file(tmp_path, language, data)
    TextsProvider.provider_init(language, tmp_path)
    assert TextsProvider.UI_TEXTS == {}

def test_load_ui_texts_missing_path(tmp_path: Path) -> None:
    TextsProvider.provider_init("en_GB", tmp_path)
    assert TextsProvider.UI_TEXTS == {}