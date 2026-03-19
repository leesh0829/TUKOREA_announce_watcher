from __future__ import annotations

from typing import Any

from announce_watcher.config import build_adapter
from announce_watcher.models import SiteConfig
from announce_watcher.sites.playwright_login_board import PlaywrightLoginBoardAdapter


def test_build_adapter_supports_playwright_login_board() -> None:
    adapter = build_adapter(
        SiteConfig(
            name="kdual-board-1",
            interval_seconds=300,
            adapter_type="playwright_login_board",
            settings={
                "board_url": "https://kpu.kdual.net/BBS/Board/List/S71855C704064",
            },
        )
    )

    assert isinstance(adapter, PlaywrightLoginBoardAdapter)


class _FakeLocator:
    def __init__(self, page: "_FakePage", selector: str):
        self.page = page
        self.selector = selector

    @property
    def first(self) -> "_FakeLocator":
        return self

    def fill(self, value: str) -> None:
        self.page.fills.append((self.selector, value))

    def click(self, force: bool = False) -> None:
        self.page.clicks.append((self.selector, force))
        if self.selector == "#btn_Login" and not force and self.page.fail_submit_click_once:
            self.page.fail_submit_click_once = False
            raise RuntimeError("submit click intercepted")

    def count(self) -> int:
        return self.page.selector_counts.get(self.selector, 1)

    def is_visible(self) -> bool:
        return self.page.visible_selectors.get(self.selector, True)

    def filter(self, has_text: str | None = None) -> "_FakeLocator":
        self.page.filters.append((self.selector, has_text))
        return self

    def evaluate(self, function: str) -> None:
        self.page.evaluates.append((self.selector, function))

    def inner_text(self) -> str:
        return self.page.inner_texts.get(self.selector, "")

    def get_attribute(self, name: str, timeout: int | None = None) -> str | None:
        return self.page.attributes.get((self.selector, name))


class _FakePage:
    def __init__(self) -> None:
        self.url = ""
        self.default_timeout: int | None = None
        self.goto_calls: list[tuple[str, str | None]] = []
        self.fills: list[tuple[str, str]] = []
        self.clicks: list[tuple[str, bool]] = []
        self.evaluates: list[tuple[str, str]] = []
        self.page_evaluates: list[tuple[str, object]] = []
        self.filters: list[tuple[str, str | None]] = []
        self.selector_counts: dict[str, int] = {}
        self.inner_texts: dict[str, str] = {}
        self.attributes: dict[tuple[str, str], str] = {}
        self.load_states: list[str] = []
        self.visible_selectors: dict[str, bool] = {}
        self.fail_submit_click_once = True
        self.page_evaluate_result = True

    def set_default_timeout(self, timeout: int) -> None:
        self.default_timeout = timeout

    def goto(self, url: str, wait_until: str | None = None) -> None:
        self.url = url
        self.goto_calls.append((url, wait_until))

    def locator(self, selector: str) -> _FakeLocator:
        return _FakeLocator(self, selector)

    def wait_for_load_state(self, state: str) -> None:
        self.load_states.append(state)

    def evaluate(self, function: str, arg: object) -> object:
        self.page_evaluates.append((function, arg))
        return self.page_evaluate_result


def test_login_formats_login_url_and_retries_submit_click(monkeypatch: Any) -> None:
    site = SiteConfig(
        name="kdual-board-1",
        interval_seconds=300,
        adapter_type="playwright_login_board",
        settings={
            "start_url": "https://kpu.kdual.net/BBS/Board/List/S71855C704064",
            "login_url": "https://kpu.kdual.net/Account/Index/?returnUrl={start_url}",
            "username": "user-id",
            "password": "user-password",
            "username_selector": "#logId, input[name=\"userid\"]",
            "password_selector": "#logPw, input[name=\"password\"]",
            "submit_selector": "#btn_Login",
            "login_timeout_seconds": 20,
        },
    )
    adapter = PlaywrightLoginBoardAdapter(site)
    page = _FakePage()

    monkeypatch.setattr(adapter, "_ensure_page", lambda: page)
    monkeypatch.setattr(adapter, "_submit_click_retry_exceptions", lambda: (RuntimeError,))
    monkeypatch.setattr(adapter, "_raise_if_login_failed", lambda *args: None)

    adapter.login()

    assert page.default_timeout == 20000
    assert page.goto_calls == [
        ("https://kpu.kdual.net/BBS/Board/List/S71855C704064", "networkidle"),
        (
            "https://kpu.kdual.net/Account/Index/?returnUrl=https://kpu.kdual.net/BBS/Board/List/S71855C704064",
            "networkidle",
        ),
    ]
    assert page.fills == [
        ("#logId, input[name=\"userid\"]", "user-id"),
        ("#logPw, input[name=\"password\"]", "user-password"),
    ]
    assert page.clicks == [
        ("#btn_Login", False),
        ("#btn_Login", True),
    ]
    assert page.load_states == ["networkidle"]


def test_login_skips_hidden_login_button_and_uses_login_url(monkeypatch: Any) -> None:
    site = SiteConfig(
        name="eclass-course-1",
        interval_seconds=300,
        adapter_type="playwright_login_board",
        settings={
            "start_url": "https://eclass.tukorea.ac.kr/ilos/main/main_form.acl",
            "login_url": "https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl",
            "login_button_selector": "a[href=\"/ilos/main/member/login_form.acl\"]",
            "username": "user-id",
            "password": "user-password",
            "username_selector": "input[name=\"usr_id\"]",
            "password_selector": "input[name=\"usr_pwd\"]",
            "submit_selector": "#login_btn",
            "login_timeout_seconds": 20,
        },
    )
    adapter = PlaywrightLoginBoardAdapter(site)
    page = _FakePage()
    page.visible_selectors["a[href=\"/ilos/main/member/login_form.acl\"]"] = False

    monkeypatch.setattr(adapter, "_ensure_page", lambda: page)
    monkeypatch.setattr(adapter, "_submit_click_retry_exceptions", lambda: (RuntimeError,))
    monkeypatch.setattr(adapter, "_raise_if_login_failed", lambda *args: None)

    adapter.login()

    assert ("a[href=\"/ilos/main/member/login_form.acl\"]", False) not in page.clicks
    assert page.goto_calls == [
        ("https://eclass.tukorea.ac.kr/ilos/main/main_form.acl", "networkidle"),
        ("https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl", "networkidle"),
    ]


def test_login_raises_clear_error_when_form_stays_visible(monkeypatch: Any) -> None:
    site = SiteConfig(
        name="eclass-course-1",
        interval_seconds=300,
        adapter_type="playwright_login_board",
        settings={
            "start_url": "https://eclass.tukorea.ac.kr/ilos/main/main_form.acl",
            "login_url": "https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl",
            "username": "user-id",
            "password": "user-password",
            "username_selector": "input[name=\"usr_id\"]",
            "password_selector": "input[name=\"usr_pwd\"]",
            "submit_selector": "#login_btn",
            "login_timeout_seconds": 20,
        },
    )
    adapter = PlaywrightLoginBoardAdapter(site)
    page = _FakePage()

    monkeypatch.setattr(adapter, "_ensure_page", lambda: page)
    monkeypatch.setattr(adapter, "_submit_click_retry_exceptions", lambda: (RuntimeError,))
    monkeypatch.setattr(
        adapter,
        "_click_submit_button",
        lambda locator: setattr(adapter, "_last_dialog_message", "로그인 정보가 일치하지 않습니다."),
    )

    try:
        adapter.login()
    except ValueError as exc:
        assert str(exc) == "Login failed for eclass-course-1: 로그인 정보가 일치하지 않습니다."
    else:
        raise AssertionError("expected ValueError")


def test_select_course_context_falls_back_to_main_page_course_link(monkeypatch: Any) -> None:
    site = SiteConfig(
        name="eclass-course-1",
        interval_seconds=300,
        adapter_type="playwright_login_board",
        settings={
            "course_name": "데이터구조와 알고리즘(01)",
            "current_course_selector": "#subject-span",
            "subject_change_selector": "#eclass_subject_change",
        },
    )
    adapter = PlaywrightLoginBoardAdapter(site)
    page = _FakePage()
    page.selector_counts["#subject-span"] = 0
    page.selector_counts["#eclass_subject_change"] = 0
    called: list[str] = []

    monkeypatch.setattr(
        adapter,
        "_open_course_from_main_page",
        lambda page_obj, course_name: called.append(course_name) or True,
    )

    adapter._select_course_context_if_needed(page)

    assert called == ["데이터구조와 알고리즘(01)"]


def test_open_course_from_main_page_uses_js_click() -> None:
    page = _FakePage()
    adapter = PlaywrightLoginBoardAdapter(SiteConfig(name="eclass-course-1", interval_seconds=300))

    result = adapter._open_course_from_main_page(page, "데이터구조와 알고리즘(01)")

    assert result is True
    assert len(page.page_evaluates) == 1
    assert page.page_evaluates[0][1] == "데이터구조와 알고리즘(01)"
    assert page.load_states == ["networkidle"]


def test_page_already_in_course_context_accepts_subject_change_title() -> None:
    adapter = PlaywrightLoginBoardAdapter(SiteConfig(name="eclass-course-1", interval_seconds=300))
    page = _FakePage()
    page.selector_counts["#subject-span"] = 0
    page.attributes[("#eclass_subject_change", "title")] = "데이터구조와 알고리즘(01)"

    result = adapter._page_already_in_course_context(
        page,
        "데이터구조와 알고리즘(01)",
        "#subject-span",
        "#eclass_subject_change",
    )

    assert result is True


def test_open_course_by_key_uses_eclass_room() -> None:
    page = _FakePage()
    adapter = PlaywrightLoginBoardAdapter(SiteConfig(name="eclass-course-4", interval_seconds=300))

    result = adapter._open_course_by_key(page, "N2026B2603091501")

    assert result is True
    assert len(page.page_evaluates) == 1
    assert page.page_evaluates[0][1] == "N2026B2603091501"
    assert page.load_states == ["networkidle"]
