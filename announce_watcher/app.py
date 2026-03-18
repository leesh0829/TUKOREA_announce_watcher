from __future__ import annotations

from apscheduler.schedulers.blocking import BlockingScheduler

from announce_watcher.config import build_site_adapters
from announce_watcher.engine import WatcherEngine
from announce_watcher.notifier import ConsoleNotifier
from announce_watcher.storage import SQLiteNoticeStore


def main() -> None:
    store = SQLiteNoticeStore()
    notifier = ConsoleNotifier()
    engine = WatcherEngine(store=store, notifier=notifier)
    scheduler = BlockingScheduler()

    adapters = build_site_adapters()
    for adapter in adapters:
        scheduler.add_job(
            engine.check_site,
            "interval",
            seconds=adapter.config.interval_seconds,
            args=[adapter],
            id=adapter.config.name,
            replace_existing=True,
        )

    if adapters:
        for adapter in adapters:
            engine.check_site(adapter)

    scheduler.start()


if __name__ == "__main__":
    main()
