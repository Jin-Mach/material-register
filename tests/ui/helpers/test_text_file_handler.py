from material_register.providers.paths_provider import PathsProvider
from material_register.ui.helpers.text_file_handler import TextFileHandler


def test_load_document_creates_file_when_missing(tmp_path, monkeypatch):
    document_dir = tmp_path / "documents"
    document_dir.mkdir()
    monkeypatch.setattr(PathsProvider, "documents", document_dir)
    ok, content = TextFileHandler.load_document("notes.txt")
    assert ok is True
    assert content == ""
    assert (document_dir / "notes.txt").exists()


def test_load_document_reads_existing_text(tmp_path, monkeypatch):
    document_dir = tmp_path / "documents"
    document_dir.mkdir()
    document_path = document_dir / "notes.txt"
    document_path.write_text("Hello world", encoding="utf-8")
    monkeypatch.setattr(PathsProvider, "documents", document_dir)
    ok, content = TextFileHandler.load_document("notes.txt")
    assert ok is True
    assert content == "Hello world"


def test_save_document_saves_text_to_existing_file(tmp_path, monkeypatch):
    document_dir = tmp_path / "documents"
    document_dir.mkdir()
    document_path = document_dir / "notes.txt"
    document_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(PathsProvider, "documents", document_dir)
    result = TextFileHandler.save_document("notes.txt", "Saved text")
    assert result is True
    assert document_path.read_text(encoding="utf-8") == "Saved text"


def test_save_document_returns_false_when_file_does_not_exist(tmp_path, monkeypatch):
    document_dir = tmp_path / "documents"
    document_dir.mkdir()
    monkeypatch.setattr(PathsProvider, "documents", document_dir)
    result = TextFileHandler.save_document("missing.txt", "Text")
    assert result is False
