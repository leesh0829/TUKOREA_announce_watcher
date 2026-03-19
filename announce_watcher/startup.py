from __future__ import annotations

import os
import sys
from pathlib import Path

from announce_watcher.models import StartupConfig

STARTUP_FILENAME = "announce_watcher_startup.cmd"


def get_startup_folder() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA is not set; Windows startup folder is unavailable.")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def build_startup_script(config_path: str, startup_config: StartupConfig) -> str:
    python_executable = Path(sys.executable)
    launcher = python_executable
    if startup_config.use_pythonw and python_executable.name.lower() == "python.exe":
        launcher = python_executable.with_name("pythonw.exe")

    return (
        "@echo off\n"
        f'cd /d "{Path.cwd()}"\n'
        f'"{launcher}" -m announce_watcher.app --config "{config_path}"\n'
    )


def install_startup(config_path: str, startup_config: StartupConfig) -> Path:
    startup_folder = get_startup_folder()
    startup_folder.mkdir(parents=True, exist_ok=True)
    script_path = startup_folder / STARTUP_FILENAME
    script_path.write_text(build_startup_script(config_path, startup_config), encoding="utf-8")
    return script_path


def uninstall_startup() -> bool:
    script_path = get_startup_folder() / STARTUP_FILENAME
    if not script_path.exists():
        return False
    script_path.unlink()
    return True
