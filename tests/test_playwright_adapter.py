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


def test_resolve_login_url_formats_return_url_template() -> None:
    adapter = PlaywrightLoginBoardAdapter(
        SiteConfig(
            name="kdual-board-1",
            interval_seconds=300,
            adapter_type="playwright_login_board",
            settings={
                "login_url": "https://kpu.kdual.net/Account/Index/?returnUrl={start_url}",
                "board_url": "https://kpu.kdual.net/BBS/Board/List/S71855C704064",
            },
        )
    )

    login_url = adapter._resolve_login_url("https://kpu.kdual.net/BBS/Board/List/S71855C704064")

    assert login_url == "https://kpu.kdual.net/Account/Index/?returnUrl=https://kpu.kdual.net/BBS/Board/List/S71855C704064"


def test_resolve_login_url_uses_kdual_default_when_missing() -> None:
    adapter = PlaywrightLoginBoardAdapter(
        SiteConfig(
            name="kdual-board-1",
            interval_seconds=300,
            adapter_type="playwright_login_board",
            settings={
                "board_url": "https://kpu.kdual.net/BBS/Board/List/S71855C704064",
            },
        )
    )

    login_url = adapter._resolve_login_url("https://kpu.kdual.net/BBS/Board/List/S71855C704064")

    assert login_url == "https://kpu.kdual.net/Account/Index/?returnUrl=https://kpu.kdual.net/BBS/Board/List/S71855C704064"
