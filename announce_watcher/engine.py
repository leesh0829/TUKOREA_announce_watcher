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

        existing_site_history = self.store.has_any_notices(adapter.config.name)
        should_notify = existing_site_history or adapter.config.notify_on_first_run
        new_count = 0

        for notice in notices:
            notice_key = adapter.normalize_notice_key(notice)
            if self.store.has_notice(adapter.config.name, notice_key):
                continue
            self.store.save_notice(notice)
            if should_notify:
                self.notifier.notify_new_notice(notice)
                new_count += 1

        detail = f"new={new_count}"
        if not existing_site_history and not adapter.config.notify_on_first_run:
            detail = "baseline-initialized"
        self.store.record_check(adapter.config.name, "ok", detail)
        return new_count
