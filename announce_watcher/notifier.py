from __future__ import annotations

import base64
import logging
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
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

        self._ensure_registered_app()
        script = self._build_powershell_script(notice)
        try:
            completed = self._run_powershell(script)
            if completed.stderr.strip():
                self.logger.info("Windows toast stderr: %s", completed.stderr.strip())
            if completed.stdout.strip():
                self.logger.info("Windows toast stdout: %s", completed.stdout.strip())
        except Exception as exc:  # pragma: no cover - depends on Windows runtime
            self.logger.warning("Windows toast notification failed: %s", exc)
            print(f"[WINDOWS-TOAST-ERROR] {exc}")

    def _ensure_registered_app(self) -> None:
        shortcut_path = self._shortcut_path()
        if shortcut_path.exists():
            return

        try:
            shortcut_path.parent.mkdir(parents=True, exist_ok=True)
            self._create_shortcut(shortcut_path)
            self.logger.info("Registered Windows toast shortcut: %s", shortcut_path)
        except Exception as exc:  # pragma: no cover - depends on Windows runtime
            self.logger.warning("Windows toast shortcut registration failed: %s", exc)

    def _shortcut_path(self) -> Path:
        start_menu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        return start_menu / f"{self.app_id}.lnk"

    def _create_shortcut(self, shortcut_path: Path) -> None:
        script = self._build_registration_script(shortcut_path)
        self._run_powershell(script)

    def _run_powershell(self, script: str) -> subprocess.CompletedProcess[str]:
        encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        return subprocess.run(
            [*_powershell_executable(), "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
            check=True,
            capture_output=True,
            text=True,
        )

    def _build_registration_script(self, shortcut_path: Path) -> str:
        target = _escape_ps_single_quoted(sys.executable)
        arguments = _escape_ps_single_quoted("-m announce_watcher.app")
        working_directory = _escape_ps_single_quoted(str(Path.cwd()))
        app_id = _escape_ps_single_quoted(self.app_id)
        shortcut = _escape_ps_single_quoted(str(shortcut_path))
        return f"""
$shortcutPath = '{shortcut}'
$targetPath = '{target}'
$arguments = '{arguments}'
$workingDirectory = '{working_directory}'
$appId = '{app_id}'

Add-Type -Language CSharp -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

[ComImport]
[Guid("00021401-0000-0000-C000-000000000046")]
internal class CShellLink {{ }}

[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("000214F9-0000-0000-C000-000000000046")]
internal interface IShellLinkW
{{
    void GetPath([Out, MarshalAs(UnmanagedType.LPWStr)] System.Text.StringBuilder pszFile, int cchMaxPath, IntPtr pfd, int fFlags);
    void GetIDList(out IntPtr ppidl);
    void SetIDList(IntPtr pidl);
    void GetDescription([Out, MarshalAs(UnmanagedType.LPWStr)] System.Text.StringBuilder pszName, int cchMaxName);
    void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string pszName);
    void GetWorkingDirectory([Out, MarshalAs(UnmanagedType.LPWStr)] System.Text.StringBuilder pszDir, int cchMaxPath);
    void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string pszDir);
    void GetArguments([Out, MarshalAs(UnmanagedType.LPWStr)] System.Text.StringBuilder pszArgs, int cchMaxPath);
    void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string pszArgs);
    void GetHotkey(out short pwHotkey);
    void SetHotkey(short wHotkey);
    void GetShowCmd(out int piShowCmd);
    void SetShowCmd(int iShowCmd);
    void GetIconLocation([Out, MarshalAs(UnmanagedType.LPWStr)] System.Text.StringBuilder pszIconPath, int cchIconPath, out int piIcon);
    void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string pszIconPath, int iIcon);
    void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string pszPathRel, int dwReserved);
    void Resolve(IntPtr hwnd, int fFlags);
    void SetPath([MarshalAs(UnmanagedType.LPWStr)] string pszFile);
}}

[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("0000010b-0000-0000-C000-000000000046")]
internal interface IPersistFile
{{
    void GetClassID(out Guid pClassID);
    void IsDirty();
    void Load([MarshalAs(UnmanagedType.LPWStr)] string pszFileName, uint dwMode);
    void Save([MarshalAs(UnmanagedType.LPWStr)] string pszFileName, bool fRemember);
    void SaveCompleted([MarshalAs(UnmanagedType.LPWStr)] string pszFileName);
    void GetCurFile([MarshalAs(UnmanagedType.LPWStr)] out string ppszFileName);
}}

[StructLayout(LayoutKind.Sequential, Pack = 4)]
internal struct PROPERTYKEY
{{
    public Guid fmtid;
    public uint pid;
}}

[StructLayout(LayoutKind.Explicit)]
internal struct PROPVARIANT
{{
    [FieldOffset(0)] public ushort vt;
    [FieldOffset(8)] public IntPtr pointerValue;

    public static PROPVARIANT FromString(string value)
    {{
        var prop = new PROPVARIANT();
        prop.vt = 31;
        prop.pointerValue = Marshal.StringToCoTaskMemUni(value);
        return prop;
    }}
}}

[ComImport]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
[Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
internal interface IPropertyStore
{{
    void GetCount(out uint cProps);
    void GetAt(uint iProp, out PROPERTYKEY pkey);
    void GetValue(ref PROPERTYKEY key, out PROPVARIANT pv);
    void SetValue(ref PROPERTYKEY key, ref PROPVARIANT pv);
    void Commit();
}}

public static class ToastShortcut
{{
    public static void CreateShortcut(string shortcutPath, string targetPath, string arguments, string workingDirectory, string appId)
    {{
        var link = (IShellLinkW)new CShellLink();
        link.SetPath(targetPath);
        link.SetArguments(arguments);
        link.SetWorkingDirectory(workingDirectory);
        link.SetDescription(appId);

        var appIdKey = new PROPERTYKEY
        {{
            fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"),
            pid = 5
        }};
        var value = PROPVARIANT.FromString(appId);
        try
        {{
            var propertyStore = (IPropertyStore)link;
            propertyStore.SetValue(ref appIdKey, ref value);
            propertyStore.Commit();
        }}
        finally
        {{
            if (value.pointerValue != IntPtr.Zero)
            {{
                Marshal.FreeCoTaskMem(value.pointerValue);
            }}
        }}

        ((IPersistFile)link).Save(shortcutPath, true);
    }}
}}
"@

[ToastShortcut]::CreateShortcut($shortcutPath, $targetPath, $arguments, $workingDirectory, $appId)
""".strip()

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


def _escape_ps_single_quoted(value: str) -> str:
    return value.replace("'", "''")


def _powershell_executable() -> list[str]:
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    preferred = Path(system_root) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    if preferred.exists():
        return [str(preferred)]
    return ["powershell.exe"]
