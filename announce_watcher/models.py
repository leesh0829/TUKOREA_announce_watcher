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
    settings: dict[str, Any] = field(default_factory=dict)
