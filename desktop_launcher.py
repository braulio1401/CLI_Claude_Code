import os
import sys
from pathlib import Path

from students_notifications.app import main


def _set_cwd_to_app_dir() -> None:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)


if __name__ == "__main__":
    _set_cwd_to_app_dir()
    main()
