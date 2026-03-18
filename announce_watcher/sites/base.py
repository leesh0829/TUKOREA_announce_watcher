from __future__ import annotations

from abc import ABC, abstractmethod

from announce_watcher.models import Notice, SiteConfig


class SiteAdapter(ABC):
    def __init__(self, config: SiteConfig) -> None:
        self.config = config

    def login(self) -> None:
        """Optional hook for adapters that need authentication."""

    @abstractmethod
    def fetch_notices(self) -> list[Notice]:
        """Return normalized notices for the configured site."""

    def normalize_notice_key(self, notice: Notice) -> str:
        return notice.notice_key
