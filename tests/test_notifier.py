from __future__ import annotations

import logging
import types
from pathlib import Path

from announce_watcher.models import Notice, NotifierConfig
from announce_watcher.notifier import WindowsToastNotifier, build_notifier
from announce_watcher.startup import build_startup_script
from announce_watcher.models import StartupConfig


def test_windows_toast_builds_powershell_script() -> None:
    notifier = WindowsToastNotifier(app_id="Test App")
    script = notifier._build_powershell_script(
        Notice(site_name="site", notice_key="n1", title="새 공지", url="https://example.com")
    )

    assert "새 공지" in script
    assert "https://example.com" in script
    assert "ToastNotificationManager" in script


def test_windows_toast_builds_registration_script(tmp_path: Path) -> None:
    notifier = WindowsToastNotifier(app_id="Test App")

    script = notifier._build_registration_script(tmp_path / "Test App.lnk")

    assert "ToastShortcut" in script
    assert "SetValue" in script
    assert "Test App.lnk" in script
    assert "9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3" in script


def test_windows_toast_registers_shortcut_before_sending(monkeypatch, tmp_path: Path) -> None:
    notifier = WindowsToastNotifier(app_id="Test App", logger=logging.getLogger("test"))
    notice = Notice(site_name="site", notice_key="n1", title="새 공지", url="https://example.com")
    calls: list[str] = []

    monkeypatch.setattr("announce_watcher.notifier.sys.platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setattr(
        notifier,
        "_create_shortcut",
        lambda path: (calls.append(f"shortcut:{path.name}"), path.write_text("shortcut", encoding="utf-8")),
    )

    def fake_run(cmd, check, capture_output, text):
        calls.append("toast")
        return types.SimpleNamespace(stderr="")

    monkeypatch.setattr("announce_watcher.notifier.subprocess.run", fake_run)

    notifier.notify_new_notice(notice)

    assert calls[0] == "shortcut:Test App.lnk"
    assert calls[1] == "toast"


def test_build_notifier_supports_windows_toast() -> None:
    notifier = build_notifier(NotifierConfig(type="windows_toast", enabled=True))

    assert notifier.__class__.__name__ == "CompositeNotifier"


def test_build_startup_script_uses_python_module_launcher() -> None:
    script = build_startup_script("watcher_config.json", StartupConfig(enabled=True, use_pythonw=False))

    assert "announce_watcher.app" in script
    assert "watcher_config.json" in script
