from __future__ import annotations

from announce_watcher.models import SiteConfig
from announce_watcher.sites.sample import SampleStaticSiteAdapter


def build_site_adapters() -> list[SampleStaticSiteAdapter]:
    configs = [
        SiteConfig(
            name="sample-static",
            interval_seconds=60,
            enabled=True,
            login_mode="none",
            settings={"base_url": "https://example.com/notices"},
        )
    ]
    return [SampleStaticSiteAdapter(config) for config in configs if config.enabled]
