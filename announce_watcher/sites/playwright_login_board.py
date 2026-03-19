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
        self._last_dialog_message: str | None = None

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
        self._page.on("dialog", self._handle_dialog)
        return self._page

    def login(self) -> None:
        page = self._ensure_page()
        start_url = self.config.settings.get("start_url") or self.config.settings.get("board_url")
        login_url = self._resolve_login_url(
            self.config.settings.get("login_url"),
            start_url,
        )
        login_button_selector = self.config.settings.get("login_button_selector")
        username_selector = self.config.settings.get("username_selector")
        password_selector = self.config.settings.get("password_selector")
        submit_selector = self.config.settings.get("submit_selector")
        username = self.config.settings.get("username")
        password = self.config.settings.get("password")
        wait_until = self.config.settings.get("wait_until", "networkidle")
        login_timeout_ms = int(float(self.config.settings.get("login_timeout_seconds", 20)) * 1000)
        self._last_dialog_message = None

        if username is None or password is None:
            raise ValueError("Playwright adapter requires settings.username and settings.password")
        if not username_selector or not password_selector or not submit_selector:
            raise ValueError(
                "Playwright adapter requires username_selector, password_selector, and submit_selector"
            )

        page.set_default_timeout(login_timeout_ms)
        page.goto(start_url, wait_until=wait_until)

        if login_button_selector:
            self._click_login_button_if_visible(page, str(login_button_selector))

        if login_url and page.url != login_url:
            page.goto(login_url, wait_until=wait_until)

        page.locator(username_selector).first.fill(str(username))
        page.locator(password_selector).first.fill(str(password))
        self._click_submit_button(page.locator(submit_selector).first)
        page.wait_for_load_state("networkidle")
        self._raise_if_login_failed(page, login_url, username_selector, password_selector)
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
        subject_change_selector = self.config.settings.get("subject_change_selector", "#eclass_subject_change")
        if self._page_already_in_course_context(page, str(course_name), current_course_selector, subject_change_selector):
            return

        subject_popup_selector = self.config.settings.get("subject_popup_selector", "#subject_room")
        course_item_selector = self.config.settings.get("course_item_selector", ".roomGo")
        subject_change_locator = page.locator(subject_change_selector)

        if subject_change_locator.count():
            subject_change_locator.first.click()
            page.locator(subject_popup_selector).first.wait_for(state="visible")
            page.locator(f"{subject_popup_selector} {course_item_selector}").filter(has_text=str(course_name)).first.click()
            page.wait_for_load_state("networkidle")
            return

        if self._open_course_from_main_page(page, str(course_name)):
            return

        course_key = self.config.settings.get("course_key")
        if course_key and self._open_course_by_key(page, str(course_key)):
            return

        raise ValueError(f"Could not select course context for {self.config.name}: {course_name}")

    def _click_submit_button(self, locator) -> None:
        try:
            locator.click()
        except self._submit_click_retry_exceptions():
            locator.click(force=True)

    def _raise_if_login_failed(
        self,
        page,
        login_url: str | None,
        username_selector: str,
        password_selector: str,
    ) -> None:
        if not self._login_form_still_visible(page, username_selector, password_selector):
            return
        if login_url and page.url != login_url:
            return

        detail = self._last_dialog_message or "still on login page after submit"
        raise ValueError(f"Login failed for {self.config.name}: {detail}")

    @staticmethod
    def _click_login_button_if_visible(page, selector: str) -> None:
        locator = page.locator(selector)
        if locator.count() and locator.first.is_visible():
            locator.first.click()

    @staticmethod
    def _open_course_from_main_page(page, course_name: str) -> bool:
        found = page.evaluate(
            """
            (targetCourseName) => {
              const normalize = (value) => (value || '').replace(/\\s+/g, '').trim();
              const target = normalize(targetCourseName);
              const candidates = Array.from(
                document.querySelectorAll('a.site-link, .sub_open, [onclick*="eclassRoom("], [onclick*="eclassRoom5("]')
              );

              for (const element of candidates) {
                const text = normalize(element.textContent);
                if (!text) {
                  continue;
                }
                if (text === target || text.includes(target) || target.includes(text)) {
                  element.click();
                  return true;
                }
              }
              return false;
            }
            """,
            course_name,
        )
        if not found:
            return False
        page.wait_for_load_state("networkidle")
        return True

    @staticmethod
    def _open_course_by_key(page, course_key: str) -> bool:
        found = page.evaluate(
            """
            (targetCourseKey) => {
              if (typeof window.eclassRoom !== 'function') {
                return false;
              }
              window.eclassRoom(targetCourseKey);
              return true;
            }
            """,
            course_key,
        )
        if not found:
            return False
        page.wait_for_load_state("networkidle")
        return True

    def _page_already_in_course_context(
        self,
        page,
        course_name: str,
        current_course_selector: str,
        subject_change_selector: str,
    ) -> bool:
        for selector in (current_course_selector, subject_change_selector):
            if self._locator_text_matches(page.locator(selector), course_name):
                return True
        return False

    @staticmethod
    def _locator_text_matches(locator, expected_text: str) -> bool:
        actual_text = PlaywrightLoginBoardAdapter._read_locator_text(locator)
        if actual_text is None:
            return False
        return PlaywrightLoginBoardAdapter._normalize_text(actual_text) == PlaywrightLoginBoardAdapter._normalize_text(
            expected_text
        )

    @staticmethod
    def _read_locator_text(locator) -> str | None:
        try:
            title = locator.first.get_attribute("title", timeout=1000)
            if title:
                return str(title)
            text = locator.first.inner_text(timeout=1000)
            if text:
                return str(text)
        except Exception:
            return None
        return None

    @staticmethod
    def _normalize_text(value: str) -> str:
        return "".join(str(value).split())

    @staticmethod
    def _login_form_still_visible(page, username_selector: str, password_selector: str) -> bool:
        username_locator = page.locator(username_selector).first
        password_locator = page.locator(password_selector).first
        return (
            username_locator.count() > 0
            and password_locator.count() > 0
            and username_locator.is_visible()
            and password_locator.is_visible()
        )

    @staticmethod
    def _resolve_login_url(login_url: str | None, start_url: str | None) -> str | None:
        if not login_url:
            return None
        if start_url:
            return str(login_url).replace("{start_url}", str(start_url))
        return str(login_url)

    @staticmethod
    def _submit_click_retry_exceptions() -> tuple[type[BaseException], ...]:
        from playwright.sync_api import Error, TimeoutError

        return (TimeoutError, Error)

    def _handle_dialog(self, dialog) -> None:
        self._last_dialog_message = dialog.message
        dialog.accept()

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
