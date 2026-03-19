from __future__ import annotations

import json
from pathlib import Path

from announce_watcher.models import AppConfig, LoggingConfig, NotifierConfig, SiteConfig, StartupConfig
from announce_watcher.sites.authenticated_tukorea_board import AuthenticatedTukoreaBoardAdapter
from announce_watcher.sites.base import SiteAdapter
from announce_watcher.sites.playwright_login_board import PlaywrightLoginBoardAdapter
from announce_watcher.sites.tukorea_board import TukoreaBoardAdapter

DEFAULT_CONFIG_PATH = Path("watcher_config.json")


def default_app_config() -> AppConfig:
    return AppConfig(
        db_path="watcher.db",
        logging=LoggingConfig(),
        notifier=NotifierConfig(type="console", enabled=True),
        startup=StartupConfig(enabled=False, use_pythonw=True),
        sites=(
            SiteConfig(
                name="kdual-board-1",
                interval_seconds=300,
                enabled=False,
                login_mode="browser",
                notify_on_first_run=False,
                adapter_type="playwright_login_board",
                settings={
                    "login_url": "https://kpu.kdual.net/Account/Index/?returnUrl={start_url}",
                    "start_url": "https://kpu.kdual.net/BBS/Board/List/S71855C704064",
                    "username": "your-id",
                    "password": "your-password",
                    "username_selector": "#logId, input[name=\"userid\"]",
                    "password_selector": "#logPw, input[name=\"password\"]",
                    "submit_selector": "#btn_Login",
                    "headless": True,
                    "board_url": "https://kpu.kdual.net/BBS/Board/List/S71855C704064",
                    "timeout_seconds": 20,
                    "login_timeout_seconds": 20,
                    "retries": 2,
                    "retry_backoff_seconds": 2,
                },
            ),
            SiteConfig(
                name="kdual-board-2",
                interval_seconds=300,
                enabled=False,
                login_mode="browser",
                notify_on_first_run=False,
                adapter_type="playwright_login_board",
                settings={
                    "login_url": "https://kpu.kdual.net/Account/Index/?returnUrl={start_url}",
                    "start_url": "https://kpu.kdual.net/BBS/Board/List/S71954C705054",
                    "username": "your-id",
                    "password": "your-password",
                    "username_selector": "#logId, input[name=\"userid\"]",
                    "password_selector": "#logPw, input[name=\"password\"]",
                    "submit_selector": "#btn_Login",
                    "headless": True,
                    "board_url": "https://kpu.kdual.net/BBS/Board/List/S71954C705054",
                    "timeout_seconds": 20,
                    "login_timeout_seconds": 20,
                    "retries": 2,
                    "retry_backoff_seconds": 2,
                },
            ),
            SiteConfig(
                name="contract-board-2792",
                interval_seconds=300,
                enabled=True,
                login_mode="none",
                notify_on_first_run=False,
                adapter_type="tukorea_board",
                settings={
                    "board_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do",
                    "timeout_seconds": 20,
                    "retries": 2,
                    "retry_backoff_seconds": 2,
                },
            ),
            SiteConfig(
                name="contract-board-3844",
                interval_seconds=300,
                enabled=True,
                login_mode="none",
                notify_on_first_run=False,
                adapter_type="tukorea_board",
                settings={
                    "board_url": "https://contract.tukorea.ac.kr/contract/3844/subview.do",
                    "timeout_seconds": 20,
                    "retries": 2,
                    "retry_backoff_seconds": 2,
                },
            ),
            SiteConfig(
                name="eclass-course-1",
                interval_seconds=300,
                enabled=False,
                login_mode="browser",
                notify_on_first_run=False,
                adapter_type="playwright_login_board",
                settings={
                    "login_url": "https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl",
                    "start_url": "https://eclass.tukorea.ac.kr/ilos/main/main_form.acl",
                    "login_button_selector": "a[href=\"/ilos/main/member/login_form.acl\"]",
                    "username": "your-id",
                    "password": "your-password",
                    "username_selector": "input[name=\"usr_id\"], input[type=\"text\"]",
                    "password_selector": "input[name=\"usr_pwd\"], input[type=\"password\"]",
                    "submit_selector": "#login_btn",
                    "headless": True,
                    "board_url": "https://eclass.tukorea.ac.kr/ilos/st/course/notice_list_form.acl",
                    "timeout_seconds": 20,
                    "login_timeout_seconds": 20,
                    "retries": 2,
                    "retry_backoff_seconds": 2,
                },
            ),
            SiteConfig(
                name="eclass-zoom-1",
                interval_seconds=300,
                enabled=False,
                login_mode="browser",
                notify_on_first_run=False,
                adapter_type="playwright_login_board",
                settings={
                    "login_url": "https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl",
                    "start_url": "https://eclass.tukorea.ac.kr/ilos/main/main_form.acl",
                    "login_button_selector": "a[href=\"/ilos/main/member/login_form.acl\"]",
                    "username": "your-id",
                    "password": "your-password",
                    "username_selector": "input[name=\"usr_id\"], input[type=\"text\"]",
                    "password_selector": "input[name=\"usr_pwd\"], input[type=\"password\"]",
                    "submit_selector": "#login_btn",
                    "headless": True,
                    "board_url": "https://eclass.tukorea.ac.kr/ilos/st/course/zoom_list_form.acl",
                    "timeout_seconds": 20,
                    "login_timeout_seconds": 20,
                    "retries": 2,
                    "retry_backoff_seconds": 2,
                },
            ),
            SiteConfig(
                name="eclass-course-2",
                interval_seconds=300,
                enabled=False,
                login_mode="browser",
                notify_on_first_run=False,
                adapter_type="playwright_login_board",
                settings={
                    "login_url": "https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl",
                    "start_url": "https://eclass.tukorea.ac.kr/ilos/main/main_form.acl",
                    "login_button_selector": "a[href=\"/ilos/main/member/login_form.acl\"]",
                    "username": "your-id",
                    "password": "your-password",
                    "username_selector": "input[name=\"usr_id\"], input[type=\"text\"]",
                    "password_selector": "input[name=\"usr_pwd\"], input[type=\"password\"]",
                    "submit_selector": "#login_btn",
                    "headless": True,
                    "board_url": "https://eclass.tukorea.ac.kr/ilos/st/course/notice_list_form.acl",
                    "timeout_seconds": 20,
                    "login_timeout_seconds": 20,
                    "retries": 2,
                    "retry_backoff_seconds": 2,
                },
            ),
            SiteConfig(
                name="eclass-course-3",
                interval_seconds=300,
                enabled=False,
                login_mode="browser",
                notify_on_first_run=False,
                adapter_type="playwright_login_board",
                settings={
                    "login_url": "https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl",
                    "start_url": "https://eclass.tukorea.ac.kr/ilos/main/main_form.acl",
                    "login_button_selector": "a[href=\"/ilos/main/member/login_form.acl\"]",
                    "username": "your-id",
                    "password": "your-password",
                    "username_selector": "input[name=\"usr_id\"], input[type=\"text\"]",
                    "password_selector": "input[name=\"usr_pwd\"], input[type=\"password\"]",
                    "submit_selector": "#login_btn",
                    "headless": True,
                    "board_url": "https://eclass.tukorea.ac.kr/ilos/st/course/notice_list_form.acl",
                    "timeout_seconds": 20,
                    "login_timeout_seconds": 20,
                    "retries": 2,
                    "retry_backoff_seconds": 2,
                },
            ),
            SiteConfig(
                name="eclass-course-4",
                interval_seconds=300,
                enabled=False,
                login_mode="browser",
                notify_on_first_run=False,
                adapter_type="playwright_login_board",
                settings={
                    "login_url": "https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl",
                    "start_url": "https://eclass.tukorea.ac.kr/ilos/main/main_form.acl",
                    "login_button_selector": "a[href=\"/ilos/main/member/login_form.acl\"]",
                    "username": "your-id",
                    "password": "your-password",
                    "username_selector": "input[name=\"usr_id\"], input[type=\"text\"]",
                    "password_selector": "input[name=\"usr_pwd\"], input[type=\"password\"]",
                    "submit_selector": "#login_btn",
                    "headless": True,
                    "board_url": "https://eclass.tukorea.ac.kr/ilos/st/course/notice_list_form.acl",
                    "timeout_seconds": 20,
                    "login_timeout_seconds": 20,
                    "retries": 2,
                    "retry_backoff_seconds": 2,
                },
            ),
        ),
    )


def app_config_to_dict(config: AppConfig) -> dict:
    return {
        "db_path": config.db_path,
        "logging": {
            "path": config.logging.path,
            "level": config.logging.level,
            "max_bytes": config.logging.max_bytes,
            "backup_count": config.logging.backup_count,
        },
        "notifier": {
            "type": config.notifier.type,
            "enabled": config.notifier.enabled,
        },
        "startup": {
            "enabled": config.startup.enabled,
            "use_pythonw": config.startup.use_pythonw,
        },
        "sites": [
            {
                "name": site.name,
                "interval_seconds": site.interval_seconds,
                "enabled": site.enabled,
                "login_mode": site.login_mode,
                "notify_on_first_run": site.notify_on_first_run,
                "adapter_type": site.adapter_type,
                "settings": site.settings,
            }
            for site in config.sites
        ],
    }


def ensure_example_config(path: Path = DEFAULT_CONFIG_PATH) -> Path:
    if path.exists():
        return path
    path.write_text(json.dumps(app_config_to_dict(default_app_config()), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_app_config(path: str | Path | None = None) -> AppConfig:
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return default_app_config()

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    sites = tuple(
        SiteConfig(
            name=site["name"],
            interval_seconds=int(site.get("interval_seconds", 300)),
            enabled=bool(site.get("enabled", True)),
            login_mode=str(site.get("login_mode", "none")),
            notify_on_first_run=bool(site.get("notify_on_first_run", False)),
            adapter_type=str(site.get("adapter_type", "tukorea_board")),
            settings=dict(site.get("settings", {})),
        )
        for site in raw.get("sites", [])
    )
    logging_config = raw.get("logging", {})
    notifier_config = raw.get("notifier", {})
    startup_config = raw.get("startup", {})
    return AppConfig(
        db_path=str(raw.get("db_path", "watcher.db")),
        logging=LoggingConfig(
            path=str(logging_config.get("path", "logs/announce_watcher.log")),
            level=str(logging_config.get("level", "INFO")),
            max_bytes=int(logging_config.get("max_bytes", 1_048_576)),
            backup_count=int(logging_config.get("backup_count", 3)),
        ),
        notifier=NotifierConfig(
            type=str(notifier_config.get("type", "console")),
            enabled=bool(notifier_config.get("enabled", True)),
        ),
        startup=StartupConfig(
            enabled=bool(startup_config.get("enabled", False)),
            use_pythonw=bool(startup_config.get("use_pythonw", True)),
        ),
        sites=sites,
    )


def build_site_adapters(app_config: AppConfig) -> list[SiteAdapter]:
    adapters: list[SiteAdapter] = []
    for site in app_config.sites:
        if not site.enabled:
            continue
        adapters.append(build_adapter(site))
    return adapters


def build_adapter(site_config: SiteConfig) -> SiteAdapter:
    if site_config.adapter_type == "tukorea_board":
        return TukoreaBoardAdapter(site_config)
    if site_config.adapter_type == "authenticated_tukorea_board":
        return AuthenticatedTukoreaBoardAdapter(site_config)
    if site_config.adapter_type == "playwright_login_board":
        return PlaywrightLoginBoardAdapter(site_config)
    raise ValueError(f"Unsupported adapter_type: {site_config.adapter_type}")
