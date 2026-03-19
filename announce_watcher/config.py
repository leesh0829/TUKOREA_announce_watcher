from __future__ import annotations

import json
from pathlib import Path

from announce_watcher.models import AppConfig, SiteConfig
from announce_watcher.sites.base import SiteAdapter
from announce_watcher.sites.tukorea_board import TukoreaBoardAdapter

DEFAULT_CONFIG_PATH = Path("watcher_config.json")


def default_app_config() -> AppConfig:
    return AppConfig(
        db_path="watcher.db",
        sites=(
            SiteConfig(
                name="tukorea-contract-notices",
                interval_seconds=300,
                enabled=True,
                login_mode="none",
                notify_on_first_run=False,
                adapter_type="tukorea_board",
                settings={
                    "board_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do",
                    "timeout_seconds": 20,
                },
            ),
        ),
    )


def app_config_to_dict(config: AppConfig) -> dict:
    return {
        "db_path": config.db_path,
        "sites": [
            {
                "name": site.name,
                "interval_seconds": site.interval_seconds,
                "enabled": site.enabled,
                "login_mode": site.login_mode,
                "notify_on_first_run": site.notify_on_first_run,
                "adapter_type": site.adapter_type,
                "settings": site.settings,
            }
            for site in config.sites
        ],
    }


def ensure_example_config(path: Path = DEFAULT_CONFIG_PATH) -> Path:
    if path.exists():
        return path
    path.write_text(json.dumps(app_config_to_dict(default_app_config()), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_app_config(path: str | Path | None = None) -> AppConfig:
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return default_app_config()

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    sites = tuple(
        SiteConfig(
            name=site["name"],
            interval_seconds=int(site.get("interval_seconds", 300)),
            enabled=bool(site.get("enabled", True)),
            login_mode=str(site.get("login_mode", "none")),
            notify_on_first_run=bool(site.get("notify_on_first_run", False)),
            adapter_type=str(site.get("adapter_type", "tukorea_board")),
            settings=dict(site.get("settings", {})),
        )
        for site in raw.get("sites", [])
    )
    return AppConfig(db_path=str(raw.get("db_path", "watcher.db")), sites=sites)


def build_site_adapters(app_config: AppConfig) -> list[SiteAdapter]:
    adapters: list[SiteAdapter] = []
    for site in app_config.sites:
        if not site.enabled:
            continue
        adapters.append(build_adapter(site))
    return adapters


def build_adapter(site_config: SiteConfig) -> SiteAdapter:
    if site_config.adapter_type == "tukorea_board":
        return TukoreaBoardAdapter(site_config)
    raise ValueError(f"Unsupported adapter_type: {site_config.adapter_type}")
