from __future__ import annotations

import hashlib
import re
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import ProxyHandler, Request, build_opener

from announce_watcher.models import Notice
from announce_watcher.sites.base import SiteAdapter


class _BoardAnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[tuple[str, str, str]] = []
        self._in_anchor = False
        self._anchor_href = ""
        self._anchor_text_parts: list[str] = []
        self._current_item_text_parts: list[str] = []
        self._pending_href = ""
        self._pending_title = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "li":
            self._current_item_text_parts = []
            self._pending_href = ""
            self._pending_title = ""
            return

        if tag != "a":
            return

        attr_map = dict(attrs)
        href = (attr_map.get("href") or "").strip()
        if "artclView.do" not in href:
            return

        self._in_anchor = True
        self._anchor_href = href
        self._anchor_text_parts = []

    def handle_data(self, data: str) -> None:
        self._current_item_text_parts.append(data)
        if self._in_anchor:
            self._anchor_text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_anchor:
            self._pending_title = self._clean_text("".join(self._anchor_text_parts))
            self._pending_href = self._anchor_href
            self._in_anchor = False
            self._anchor_href = ""
            self._anchor_text_parts = []

        if tag == "li":
            context = self._clean_text("".join(self._current_item_text_parts))
            if self._pending_title and self._pending_href:
                self.items.append((self._pending_href, self._pending_title, context))
            self._current_item_text_parts = []
            self._pending_href = ""
            self._pending_title = ""

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()


class TukoreaBoardAdapter(SiteAdapter):
    """HTTP-based adapter for TUKOREA K2Web board pages."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Safari/537.36"
        )
    }

    def fetch_notices(self) -> list[Notice]:
        board_url = self.config.settings["board_url"]
        timeout_seconds = float(self.config.settings.get("timeout_seconds", 20))
        request = Request(board_url, headers=self.DEFAULT_HEADERS)
        opener = build_opener(ProxyHandler({}))
        with opener.open(request, timeout=timeout_seconds) as response:
            html = response.read().decode("utf-8", "ignore")
        return self.parse_notice_list(html, board_url)

    def parse_notice_list(self, html: str, board_url: str) -> list[Notice]:
        parser = _BoardAnchorParser()
        parser.feed(html)

        notices: list[Notice] = []
        seen_keys: set[str] = set()
        for href, title, context in parser.items:
            notice_url = urljoin(board_url, href)
            notice_key = self._extract_notice_key(notice_url)
            if notice_key in seen_keys:
                continue

            notices.append(
                Notice(
                    site_name=self.config.name,
                    notice_key=notice_key,
                    title=title,
                    url=notice_url,
                    published_at=self._extract_published_at(context),
                )
            )
            seen_keys.add(notice_key)

        return notices

    @staticmethod
    def _extract_published_at(context: str) -> datetime | None:
        match = re.search(r"등록일\s*(\d{4}\.\d{2}\.\d{2})", context)
        if not match:
            return None
        return datetime.strptime(match.group(1), "%Y.%m.%d")

    @staticmethod
    def _extract_notice_key(notice_url: str) -> str:
        path_match = re.search(r"/(\d+)/artclView\.do", notice_url)
        if path_match:
            return path_match.group(1)

        query_match = re.search(r"[?&]artclSeq=(\d+)", notice_url)
        if query_match:
            return query_match.group(1)

        return hashlib.sha256(notice_url.encode("utf-8")).hexdigest()[:16]
