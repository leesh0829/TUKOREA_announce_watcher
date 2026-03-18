from __future__ import annotations

from abc import ABC, abstractmethod

from announce_watcher.models import Notice


class Notifier(ABC):
    @abstractmethod
    def notify_new_notice(self, notice: Notice) -> None:
        """Emit a user-visible notification for a new notice."""


class ConsoleNotifier(Notifier):
    def notify_new_notice(self, notice: Notice) -> None:
        print(f"[NEW] {notice.site_name}: {notice.title} -> {notice.url}")
