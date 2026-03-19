from __future__ import annotations

import json
from pathlib import Path

from announce_watcher.app import parse_args
from announce_watcher.config import app_config_to_dict, default_app_config, ensure_example_config, load_app_config


def test_load_app_config_returns_defaults_when_file_missing(tmp_path: Path) -> None:
    config = load_app_config(tmp_path / "missing.json")

    assert config.db_path == "watcher.db"
    assert len(config.sites) == 1
    assert config.sites[0].name == "tukorea-contract-notices"


def test_load_app_config_reads_json_file(tmp_path: Path) -> None:
    path = tmp_path / "watcher_config.json"
    path.write_text(
        json.dumps(
            {
                "db_path": "custom.db",
                "notifier": {"type": "windows_toast", "enabled": True},
                "logging": {"path": "logs/custom.log", "level": "DEBUG", "max_bytes": 2048, "backup_count": 5},
                "startup": {"enabled": True, "use_pythonw": False},
                "sites": [
                    {
                        "name": "board-a",
                        "interval_seconds": 120,
                        "enabled": True,
                        "adapter_type": "tukorea_board",
                        "notify_on_first_run": True,
                        "settings": {"board_url": "https://example.com/board"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config = load_app_config(path)

    assert config.db_path == "custom.db"
    assert len(config.sites) == 1
    assert config.notifier.type == "windows_toast"
    assert config.logging.level == "DEBUG"
    assert config.startup.enabled is True
    assert config.sites[0].notify_on_first_run is True
    assert config.sites[0].settings["board_url"] == "https://example.com/board"


def test_ensure_example_config_writes_starter_file(tmp_path: Path) -> None:
    path = ensure_example_config(tmp_path / "watcher_config.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload == app_config_to_dict(default_app_config())


def test_parse_args_supports_once_and_config() -> None:
    args = parse_args(["--config", "custom.json", "--once"])

    assert args.config == "custom.json"
    assert args.once is True
