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
        self.close_calls = 0

    def fetch_notices(self) -> list[Notice]:
        return self._notices

    def close(self) -> None:
        self.close_calls += 1


def test_engine_initial_run_builds_baseline_without_notification(tmp_path: Path) -> None:
    store = SQLiteNoticeStore(tmp_path / "watcher.db")
    notifier = MemoryNotifier()
    engine = WatcherEngine(store=store, notifier=notifier)
    config = SiteConfig(name="test-site", interval_seconds=60)
    notice = Notice(site_name="test-site", notice_key="n1", title="Hello", url="https://example.com")
    adapter = FakeAdapter(config, [notice])

    first_count = engine.check_site(adapter)
    second_count = engine.check_site(adapter)

    assert first_count == 0
    assert second_count == 0
    assert notifier.messages == []
    assert adapter.close_calls == 2


def test_engine_notifies_only_for_new_notices_after_baseline(tmp_path: Path) -> None:
    store = SQLiteNoticeStore(tmp_path / "watcher.db")
    notifier = MemoryNotifier()
    engine = WatcherEngine(store=store, notifier=notifier)
    config = SiteConfig(name="test-site", interval_seconds=60)
    baseline_notice = Notice(site_name="test-site", notice_key="n1", title="Hello", url="https://example.com/1")
    new_notice = Notice(site_name="test-site", notice_key="n2", title="World", url="https://example.com/2")

    engine.check_site(FakeAdapter(config, [baseline_notice]))
    count = engine.check_site(FakeAdapter(config, [baseline_notice, new_notice]))

    assert count == 1
    assert notifier.messages == ["n2"]


def test_engine_can_notify_on_first_run_when_opted_in(tmp_path: Path) -> None:
    store = SQLiteNoticeStore(tmp_path / "watcher.db")
    notifier = MemoryNotifier()
    engine = WatcherEngine(store=store, notifier=notifier)
    config = SiteConfig(name="test-site", interval_seconds=60, notify_on_first_run=True)
    notice = Notice(site_name="test-site", notice_key="n1", title="Hello", url="https://example.com")

    count = engine.check_site(FakeAdapter(config, [notice]))

    assert count == 1
    assert notifier.messages == ["n1"]


def test_engine_closes_adapter_after_fetch_error(tmp_path: Path) -> None:
    class FailingAdapter(FakeAdapter):
        def fetch_notices(self) -> list[Notice]:
            raise ValueError("boom")

    store = SQLiteNoticeStore(tmp_path / "watcher.db")
    notifier = MemoryNotifier()
    engine = WatcherEngine(store=store, notifier=notifier)
    adapter = FailingAdapter(SiteConfig(name="test-site", interval_seconds=60), [])

    try:
        engine.check_site(adapter)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

    assert adapter.close_calls == 1
