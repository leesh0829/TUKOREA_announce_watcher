from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from urllib.error import URLError

from announce_watcher.models import Notice, SiteConfig


class SiteAdapter(ABC):
    def __init__(self, config: SiteConfig) -> None:
        self.config = config
        self.logger = logging.getLogger("announce_watcher")

    def login(self) -> None:
        """Optional hook for adapters that need authentication."""

    def close(self) -> None:
        """Optional hook for adapters that need cleanup after a check."""

    @abstractmethod
    def fetch_notices(self) -> list[Notice]:
        """Return normalized notices for the configured site."""

    def normalize_notice_key(self, notice: Notice) -> str:
        return notice.notice_key

    def fetch_notices_with_retry(self) -> list[Notice]:
        retries = int(self.config.settings.get("retries", 2))
        backoff_seconds = float(self.config.settings.get("retry_backoff_seconds", 2))

        for attempt in range(retries + 1):
            try:
                return self.fetch_notices()
            except (TimeoutError, URLError, OSError, ValueError) as exc:
                if attempt >= retries:
                    raise
                sleep_seconds = backoff_seconds * (attempt + 1)
                self.logger.warning(
                    "Fetch failed for %s (attempt %s/%s): %s; retrying in %.1fs",
                    self.config.name,
                    attempt + 1,
                    retries + 1,
                    exc,
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)
