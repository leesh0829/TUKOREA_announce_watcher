from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True, frozen=True)
class Notice:
    site_name: str
    notice_key: str
    title: str
    url: str
    published_at: datetime | None = None
    first_seen_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True, frozen=True)
class SiteConfig:
    name: str
    interval_seconds: int
    enabled: bool = True
    login_mode: str = "none"
    notify_on_first_run: bool = False
    adapter_type: str = "tukorea_board"
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class LoggingConfig:
    path: str = "logs/announce_watcher.log"
    level: str = "INFO"
    max_bytes: int = 1_048_576
    backup_count: int = 3


@dataclass(slots=True, frozen=True)
class NotifierConfig:
    type: str = "console"
    enabled: bool = True


@dataclass(slots=True, frozen=True)
class StartupConfig:
    enabled: bool = False
    use_pythonw: bool = True


@dataclass(slots=True, frozen=True)
class AppConfig:
    db_path: str = "watcher.db"
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    notifier: NotifierConfig = field(default_factory=NotifierConfig)
    startup: StartupConfig = field(default_factory=StartupConfig)
    sites: tuple[SiteConfig, ...] = ()
