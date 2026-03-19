from __future__ import annotations

from http.cookiejar import CookieJar
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, ProxyHandler, Request, build_opener

from announce_watcher.sites.tukorea_board import TukoreaBoardAdapter


class AuthenticatedTukoreaBoardAdapter(TukoreaBoardAdapter):
    """Generic form-login variant for boards that require a session before fetching notices."""

    def __init__(self, config):
        super().__init__(config)
        self.cookie_jar = CookieJar()
        self._opener = build_opener(ProxyHandler({}), HTTPCookieProcessor(self.cookie_jar))

    def login(self) -> None:
        login_url = self.config.settings.get("login_url")
        username = self.config.settings.get("username")
        password = self.config.settings.get("password")
        username_field = self.config.settings.get("username_field", "username")
        password_field = self.config.settings.get("password_field", "password")
        extra_fields = dict(self.config.settings.get("extra_login_fields", {}))

        if not login_url:
            raise ValueError("Authenticated adapter requires settings.login_url")
        if username is None or password is None:
            raise ValueError("Authenticated adapter requires settings.username and settings.password")

        payload = {
            username_field: username,
            password_field: password,
            **extra_fields,
        }
        request = Request(
            login_url,
            data=urlencode(payload).encode("utf-8"),
            headers={**self.DEFAULT_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        )
        with self._opener.open(request, timeout=float(self.config.settings.get("login_timeout_seconds", 20))) as response:
            response.read()

    def fetch_notices(self) -> list:
        board_url = self.config.settings["board_url"]
        request = Request(board_url, headers=self.DEFAULT_HEADERS)
        with self._opener.open(request, timeout=float(self.config.settings.get("timeout_seconds", 20))) as response:
            html = response.read().decode("utf-8", "ignore")
        return self.parse_notice_list(html, board_url)
