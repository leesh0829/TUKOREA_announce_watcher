from __future__ import annotations

from datetime import datetime, timezone

from announce_watcher.models import Notice
from announce_watcher.sites.base import SiteAdapter


class SampleStaticSiteAdapter(SiteAdapter):
    """Example adapter that simulates a lightweight static site."""

    def fetch_notices(self) -> list[Notice]:
        base_url = self.config.settings.get("base_url", "https://example.com/notices")
        return [
            Notice(
                site_name=self.config.name,
                notice_key="welcome-notice",
                title="Sample notice",
                url=f"{base_url}/welcome-notice",
                published_at=datetime(2026, 3, 18, tzinfo=timezone.utc),
            )
        ]
