from __future__ import annotations

import argparse
from typing import Sequence

from announce_watcher.config import DEFAULT_CONFIG_PATH, build_site_adapters, ensure_example_config, load_app_config
from announce_watcher.engine import WatcherEngine
from announce_watcher.logging_utils import configure_logging
from announce_watcher.notifier import build_notifier
from announce_watcher.startup import install_startup, uninstall_startup
from announce_watcher.storage import SQLiteNoticeStore
from announce_watcher.tray import run_tray_app


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor TUKOREA notice boards for new posts.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to watcher JSON config file.")
    parser.add_argument("--db-path", default=None, help="Override SQLite DB path.")
    parser.add_argument("--once", action="store_true", help="Run one check cycle and exit.")
    parser.add_argument("--list-sites", action="store_true", help="Print enabled sites from config and exit.")
    parser.add_argument("--install-startup", action="store_true", help="Install Windows Startup launcher.")
    parser.add_argument("--uninstall-startup", action="store_true", help="Remove Windows Startup launcher.")
    parser.add_argument("--tray", action="store_true", help="Run tray icon mode (requires optional pystray/Pillow).")
    parser.add_argument(
        "--write-example-config",
        action="store_true",
        help="Write a starter watcher_config.json if it does not exist, then exit.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)

    if args.write_example_config:
        path = ensure_example_config()
        print(f"Wrote example config: {path}")
        return

    app_config = load_app_config(args.config)
    logger = configure_logging(app_config.logging)

    if args.install_startup:
        script_path = install_startup(args.config, app_config.startup)
        print(f"Installed startup launcher: {script_path}")
        return

    if args.uninstall_startup:
        removed = uninstall_startup()
        print("Removed startup launcher." if removed else "Startup launcher not found.")
        return

    if args.tray:
        run_tray_app()
        return

    db_path = args.db_path or app_config.db_path
    adapters = build_site_adapters(app_config)

    if args.list_sites:
        if not adapters:
            print("No enabled sites configured.")
            return
        for adapter in adapters:
            print(f"- {adapter.config.name}: {adapter.config.settings.get('board_url', '')}")
        return

    notifier = build_notifier(app_config.notifier, logger=logger)
    store = SQLiteNoticeStore(db_path)
    engine = WatcherEngine(store=store, notifier=notifier)

    if not adapters:
        print("No enabled sites configured.")
        return

    try:
        for adapter in adapters:
            count = engine.check_site(adapter)
            logger.info("Checked %s: %s new notices", adapter.config.name, count)
            print(f"[CHECK] {adapter.config.name}: {count} new notices")

        if args.once:
            return

        from apscheduler.schedulers.blocking import BlockingScheduler

        scheduler = BlockingScheduler()
        for adapter in adapters:
            scheduler.add_job(
                engine.check_site,
                "interval",
                seconds=adapter.config.interval_seconds,
                args=[adapter],
                id=adapter.config.name,
                replace_existing=True,
            )

        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Watcher stopped by user.")
        print("Watcher stopped.")
        return


if __name__ == "__main__":
    main()
