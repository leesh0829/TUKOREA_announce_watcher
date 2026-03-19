from __future__ import annotations

import logging
import sys
import types

from announce_watcher import app
from announce_watcher.models import AppConfig, LoggingConfig, NotifierConfig, SiteConfig, StartupConfig


class _FakeAdapter:
    def __init__(self) -> None:
        self.config = SiteConfig(name="test-site", interval_seconds=300)


class _FakeEngine:
    def __init__(self, store, notifier) -> None:
        self.store = store
        self.notifier = notifier

    def check_site(self, adapter) -> int:
        return 0


class _FakeScheduler:
    def add_job(self, *args, **kwargs) -> None:
        return None

    def start(self) -> None:
        raise KeyboardInterrupt


def test_main_handles_keyboard_interrupt_gracefully(monkeypatch, capsys) -> None:
    blocking_module = types.ModuleType("apscheduler.schedulers.blocking")
    blocking_module.BlockingScheduler = _FakeScheduler
    monkeypatch.setitem(sys.modules, "apscheduler", types.ModuleType("apscheduler"))
    monkeypatch.setitem(sys.modules, "apscheduler.schedulers", types.ModuleType("apscheduler.schedulers"))
    monkeypatch.setitem(sys.modules, "apscheduler.schedulers.blocking", blocking_module)

    monkeypatch.setattr(
        app,
        "load_app_config",
        lambda path: AppConfig(
            db_path="watcher.db",
            logging=LoggingConfig(),
            notifier=NotifierConfig(type="console", enabled=True),
            startup=StartupConfig(),
            sites=(SiteConfig(name="test-site", interval_seconds=300),),
        ),
    )
    monkeypatch.setattr(app, "configure_logging", lambda config: logging.getLogger("test"))
    monkeypatch.setattr(app, "build_site_adapters", lambda config: [_FakeAdapter()])
    monkeypatch.setattr(app, "build_notifier", lambda config, logger=None: object())
    monkeypatch.setattr(app, "SQLiteNoticeStore", lambda path: object())
    monkeypatch.setattr(app, "WatcherEngine", _FakeEngine)

    app.main([])

    captured = capsys.readouterr()
    assert "[CHECK] test-site: 0 new notices" in captured.out
    assert "Watcher stopped." in captured.out
