from __future__ import annotations

from announce_watcher.config import build_adapter
from announce_watcher.models import SiteConfig
from announce_watcher.sites.playwright_login_board import PlaywrightLoginBoardAdapter


def test_build_adapter_supports_playwright_login_board() -> None:
    adapter = build_adapter(
        SiteConfig(
            name="kdual-board-1",
            interval_seconds=300,
            adapter_type="playwright_login_board",
            settings={
                "board_url": "https://kpu.kdual.net/BBS/Board/List/S71855C704064",
            },
        )
    )

    assert isinstance(adapter, PlaywrightLoginBoardAdapter)
