from __future__ import annotations

from announce_watcher.models import SiteConfig
from announce_watcher.sites.tukorea_board import TukoreaBoardAdapter


def build_site_adapters() -> list[TukoreaBoardAdapter]:
    configs = [
        SiteConfig(
            name="tukorea-contract-notices",
            interval_seconds=300,
            enabled=True,
            login_mode="none",
            notify_on_first_run=False,
            settings={
                "board_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do",
                "timeout_seconds": 20,
            },
        )
    ]
    return [TukoreaBoardAdapter(config) for config in configs if config.enabled]
