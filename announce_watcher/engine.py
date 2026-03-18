from __future__ import annotations

from announce_watcher.notifier import Notifier
from announce_watcher.sites.base import SiteAdapter
from announce_watcher.storage import SQLiteNoticeStore


class WatcherEngine:
    def __init__(self, store: SQLiteNoticeStore, notifier: Notifier) -> None:
        self.store = store
        self.notifier = notifier

    def check_site(self, adapter: SiteAdapter) -> int:
        try:
            adapter.login()
            notices = adapter.fetch_notices()
        except Exception as exc:  # pragma: no cover - defensive logging path
            self.store.record_check(adapter.config.name, "error", str(exc))
            raise

        new_count = 0
        for notice in notices:
            notice_key = adapter.normalize_notice_key(notice)
            if self.store.has_notice(adapter.config.name, notice_key):
                continue
            self.store.save_notice(notice)
            self.notifier.notify_new_notice(notice)
            new_count += 1

        self.store.record_check(adapter.config.name, "ok", f"new={new_count}")
        return new_count
