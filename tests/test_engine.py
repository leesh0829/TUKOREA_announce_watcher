from __future__ import annotations

from pathlib import Path

from announce_watcher.engine import WatcherEngine
from announce_watcher.models import Notice, SiteConfig
from announce_watcher.notifier import Notifier
from announce_watcher.sites.base import SiteAdapter
from announce_watcher.storage import SQLiteNoticeStore


class MemoryNotifier(Notifier):
    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify_new_notice(self, notice: Notice) -> None:
        self.messages.append(notice.notice_key)


class FakeAdapter(SiteAdapter):
    def __init__(self, config: SiteConfig, notices: list[Notice]) -> None:
        super().__init__(config)
        self._notices = notices

    def fetch_notices(self) -> list[Notice]:
        return self._notices


def test_engine_only_notifies_for_new_notices(tmp_path: Path) -> None:
    store = SQLiteNoticeStore(tmp_path / "watcher.db")
    notifier = MemoryNotifier()
    engine = WatcherEngine(store=store, notifier=notifier)
    config = SiteConfig(name="test-site", interval_seconds=60)
    notice = Notice(site_name="test-site", notice_key="n1", title="Hello", url="https://example.com")
    adapter = FakeAdapter(config, [notice])

    first_count = engine.check_site(adapter)
    second_count = engine.check_site(adapter)

    assert first_count == 1
    assert second_count == 0
    assert notifier.messages == ["n1"]
