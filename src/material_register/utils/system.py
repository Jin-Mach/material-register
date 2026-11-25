import os
import sys
import uuid
from pathlib import Path


def is_disk_writable(test_path: Path) -> bool:
    test_file = test_path / f"test_{uuid.uuid4().hex}.txt"
    try:
        test_file.write_text("test text")
        test_file.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def restart_application(info: str = "") -> None:
    executable_file = sys.executable
    args = [*sys.argv]
    if info:
        args.append(info)
    os.execl(executable_file, executable_file, *args)
