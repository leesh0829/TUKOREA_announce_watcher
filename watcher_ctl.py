from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
LOGS_DIR = PROJECT_ROOT / "logs"
PID_FILE = LOGS_DIR / "announce_watcher.pid"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start/stop/status helper for announce watcher.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start watcher in background.")
    start_parser.add_argument("--config", default="watcher_config.json")
    start_parser.add_argument("--show-console", action="store_true")

    subparsers.add_parser("stop", help="Stop watcher.")
    subparsers.add_parser("status", help="Show watcher status.")
    return parser.parse_args()


def resolve_python(show_console: bool) -> Path:
    pythonw = PROJECT_ROOT / ".venv" / "Scripts" / "pythonw.exe"
    python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

    if not show_console and pythonw.exists():
        return pythonw
    if python.exists():
        return python
    if pythonw.exists():
        return pythonw
    raise SystemExit(f"Python launcher not found: {python}")


def read_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    raw = PID_FILE.read_text(encoding="ascii").strip()
    if not raw:
        PID_FILE.unlink(missing_ok=True)
        return None
    try:
        return int(raw)
    except ValueError:
        PID_FILE.unlink(missing_ok=True)
        return None


def is_running(pid: int) -> bool:
    completed = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout.strip()
    return bool(output) and not output.startswith("INFO:")


def write_pid(pid: int) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid), encoding="ascii")


def remove_pid_file() -> None:
    PID_FILE.unlink(missing_ok=True)


def start_watcher(config_path: str, show_console: bool) -> int:
    existing_pid = read_pid()
    if existing_pid and is_running(existing_pid):
        print(f"Watcher is already running. PID: {existing_pid}")
        return 0
    remove_pid_file()

    resolved_config = Path(config_path)
    if not resolved_config.is_absolute():
        resolved_config = PROJECT_ROOT / resolved_config
    if not resolved_config.exists():
        raise SystemExit(f"Config file not found: {resolved_config}")

    launcher = resolve_python(show_console)
    args = [str(launcher), "-m", "announce_watcher.app", "--config", str(resolved_config)]

    creationflags = 0
    if os.name == "nt":
        creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        if not show_console:
            creationflags |= getattr(subprocess, "DETACHED_PROCESS", 0)
            creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)

    process = subprocess.Popen(
        args,
        cwd=PROJECT_ROOT,
        creationflags=creationflags,
        stdout=subprocess.DEVNULL if not show_console else None,
        stderr=subprocess.DEVNULL if not show_console else None,
    )
    time.sleep(0.7)
    if process.poll() is not None:
        raise SystemExit("Watcher exited immediately. Check logs/announce_watcher.log for details.")

    write_pid(process.pid)
    print(f"Watcher started. PID: {process.pid}")
    print(r"Status: .\status-watcher.ps1")
    print(r"Stop:   .\stop-watcher.ps1")
    return 0


def stop_watcher() -> int:
    pid = read_pid()
    if not pid:
        print("Watcher is not running.")
        return 0
    if not is_running(pid):
        remove_pid_file()
        print("Watcher is not running.")
        return 0

    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True, text=True)
    time.sleep(0.3)
    remove_pid_file()
    print(f"Watcher stopped. PID: {pid}")
    return 0


def status_watcher() -> int:
    pid = read_pid()
    if not pid:
        print("Watcher is not running.")
        return 0
    if not is_running(pid):
        remove_pid_file()
        print("Watcher is not running.")
        return 0
    print(f"Watcher is running. PID: {pid}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "start":
        return start_watcher(args.config, args.show_console)
    if args.command == "stop":
        return stop_watcher()
    return status_watcher()


if __name__ == "__main__":
    raise SystemExit(main())
