from types import SimpleNamespace

import requests

from material_register.providers.download_provider import DownloadProvider


def _fake_response_text(*args, **kwargs):
    return SimpleNamespace(
        text='{"ok": true}', content=b"", raise_for_status=lambda: None
    )


def _fake_response_binary(*args, **kwargs):
    return SimpleNamespace(
        text="", content=b"binary-data", raise_for_status=lambda: None
    )


def test_save_text_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(requests, "get", _fake_response_text)
    path = tmp_path / "en_GB/ui_texts.json"
    result = DownloadProvider._save_file("https://fake-url", path)
    assert result is True
    assert path.read_text() == '{"ok": true}'


def test_save_icon_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(requests, "get", _fake_response_binary)
    path = tmp_path / "icon.png"
    result = DownloadProvider._save_file("https://fake-url", path)
    assert result is True
    assert path.read_bytes() == b"binary-data"


def test_download_files_success(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(requests, "get", _fake_response_text)
    invalid_files = {tmp_path / "en_GB/ui_texts.json"}
    result = DownloadProvider.download_files(invalid_files, tmp_path)
    assert result is True
