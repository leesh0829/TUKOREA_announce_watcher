from __future__ import annotations

from announce_watcher.sites.tukorea_board import TukoreaBoardAdapter


class PlaywrightLoginBoardAdapter(TukoreaBoardAdapter):
    """Browser automation adapter for multi-step login flows such as KDUAL/eclass."""

    def __init__(self, config):
        super().__init__(config)
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    def _ensure_page(self):
        if self._page is not None:
            return self._page

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover - optional dependency path
            raise RuntimeError(
                "Playwright adapter requires 'playwright'. Install it and run 'playwright install chromium'."
            ) from exc

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=bool(self.config.settings.get("headless", True))
        )
        self._context = self._browser.new_context()
        self._page = self._context.new_page()
        self._page.on("dialog", lambda dialog: dialog.accept())
        return self._page

    def login(self) -> None:
        page = self._ensure_page()
        start_url = self.config.settings.get("start_url") or self.config.settings.get("board_url")
        login_url = self.config.settings.get("login_url")
        login_button_selector = self.config.settings.get("login_button_selector")
        username_selector = self.config.settings.get("username_selector")
        password_selector = self.config.settings.get("password_selector")
        submit_selector = self.config.settings.get("submit_selector")
        username = self.config.settings.get("username")
        password = self.config.settings.get("password")
        wait_until = self.config.settings.get("wait_until", "networkidle")

        if username is None or password is None:
            raise ValueError("Playwright adapter requires settings.username and settings.password")
        if not username_selector or not password_selector or not submit_selector:
            raise ValueError(
                "Playwright adapter requires username_selector, password_selector, and submit_selector"
            )

        page.goto(start_url, wait_until=wait_until)

        if login_button_selector:
            page.locator(login_button_selector).first.click()

        if login_url and page.url != login_url:
            page.goto(login_url, wait_until=wait_until)

        page.locator(username_selector).first.fill(str(username))
        page.locator(password_selector).first.fill(str(password))
        page.locator(submit_selector).first.click()
        page.wait_for_load_state("networkidle")
        self._select_course_context_if_needed(page)

    def fetch_notices(self) -> list:
        page = self._ensure_page()
        self._select_course_context_if_needed(page)
        board_url = self.config.settings["board_url"]
        page.goto(board_url, wait_until=self.config.settings.get("wait_until", "networkidle"))
        return self.parse_notice_list(page.content(), board_url)

    def _select_course_context_if_needed(self, page) -> None:
        course_name = self.config.settings.get("course_name")
        if not course_name:
            return

        current_course_selector = self.config.settings.get("current_course_selector", "#subject-span")
        current_course_locator = page.locator(current_course_selector)
        if current_course_locator.count() and current_course_locator.first.inner_text().strip() == str(course_name):
            return

        subject_change_selector = self.config.settings.get("subject_change_selector", "#eclass_subject_change")
        subject_popup_selector = self.config.settings.get("subject_popup_selector", "#subject_room")
        course_item_selector = self.config.settings.get("course_item_selector", ".roomGo")

        page.locator(subject_change_selector).first.click()
        page.locator(subject_popup_selector).first.wait_for(state="visible")
        page.locator(f"{subject_popup_selector} {course_item_selector}").filter(has_text=str(course_name)).first.click()
        page.wait_for_load_state("networkidle")

    def close(self) -> None:
        if self._context is not None:
            self._context.close()
            self._context = None
        if self._browser is not None:
            self._browser.close()
            self._browser = None
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None
        self._page = None
