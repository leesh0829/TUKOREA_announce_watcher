from __future__ import annotations

import base64
import logging
import subprocess
import sys
from abc import ABC, abstractmethod
from typing import Iterable

from announce_watcher.models import Notice, NotifierConfig


class Notifier(ABC):
    @abstractmethod
    def notify_new_notice(self, notice: Notice) -> None:
        """Emit a user-visible notification for a new notice."""


class ConsoleNotifier(Notifier):
    def notify_new_notice(self, notice: Notice) -> None:
        print(f"[NEW] {notice.site_name}: {notice.title} -> {notice.url}")


class WindowsToastNotifier(Notifier):
    def __init__(self, app_id: str = "TUKOREA Announce Watcher", logger: logging.Logger | None = None) -> None:
        self.app_id = app_id
        self.logger = logger or logging.getLogger("announce_watcher")

    def notify_new_notice(self, notice: Notice) -> None:
        if sys.platform != "win32":
            self.logger.info("Windows toast skipped on non-Windows platform: %s", notice.title)
            return

        script = self._build_powershell_script(notice)
        encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception as exc:  # pragma: no cover - depends on Windows runtime
            self.logger.warning("Windows toast notification failed: %s", exc)

    def _build_powershell_script(self, notice: Notice) -> str:
        title = _escape_ps(notice.title)
        body = _escape_ps(notice.url)
        app_id = _escape_ps(self.app_id)
        return f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>{title}</text><text>{body}</text></binding></visual></toast>")
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{app_id}').Show($toast)
""".strip()


class CompositeNotifier(Notifier):
    def __init__(self, notifiers: Iterable[Notifier]) -> None:
        self.notifiers = list(notifiers)

    def notify_new_notice(self, notice: Notice) -> None:
        for notifier in self.notifiers:
            notifier.notify_new_notice(notice)


class NullNotifier(Notifier):
    def notify_new_notice(self, notice: Notice) -> None:
        return


def build_notifier(config: NotifierConfig, logger: logging.Logger | None = None) -> Notifier:
    if not config.enabled:
        return NullNotifier()
    if config.type == "console":
        return ConsoleNotifier()
    if config.type == "windows_toast":
        return CompositeNotifier([ConsoleNotifier(), WindowsToastNotifier(logger=logger)])
    raise ValueError(f"Unsupported notifier type: {config.type}")


def _escape_ps(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&apos;")
        .replace('"', "&quot;")
    )
