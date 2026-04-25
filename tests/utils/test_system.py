from pathlib import Path

from material_register.utils.system import is_disk_writable


def _fake_write_text(*args, **kwargs) -> None:
    raise OSError

def test_is_disk_writable_valid(tmp_path) -> None:
    assert is_disk_writable(tmp_path) == True

def test_is_disk_writable_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "write_text", _fake_write_text)
    assert is_disk_writable(tmp_path) is False