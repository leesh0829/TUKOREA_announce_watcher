from __future__ import annotations

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


def test_build_notifier_supports_windows_toast() -> None:
    notifier = build_notifier(NotifierConfig(type="windows_toast", enabled=True))

    assert notifier.__class__.__name__ == "CompositeNotifier"


def test_build_startup_script_uses_python_module_launcher() -> None:
    script = build_startup_script("watcher_config.json", StartupConfig(enabled=True, use_pythonw=False))

    assert "announce_watcher.app" in script
    assert "watcher_config.json" in script
