from __future__ import annotations

from announce_watcher.models import SiteConfig
from announce_watcher.sites.tukorea_board import TukoreaBoardAdapter


SAMPLE_HTML = """
<ul>
  <li>
    <a href="/bbs/contract/285/138185/artclView.do">★중요★ 비콘 출석 안내</a>
    <span>등록일 2025.03.07</span>
  </li>
  <li>
    <a href="/bbs/contract/285/138184/artclView.do">토요일 셔틀버스 안내 (2025-1)</a>
    <span>등록일 2025.02.26</span>
  </li>
</ul>
"""


def test_tukorea_board_adapter_parses_notice_list() -> None:
    adapter = TukoreaBoardAdapter(
        SiteConfig(
            name="tukorea-contract-notices",
            interval_seconds=300,
            settings={"board_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do"},
        )
    )

    notices = adapter.parse_notice_list(SAMPLE_HTML, "https://contract.tukorea.ac.kr/contract/2792/subview.do")

    assert len(notices) == 2
    assert notices[0].notice_key == "138185"
    assert notices[0].title == "★중요★ 비콘 출석 안내"
    assert notices[0].url == "https://contract.tukorea.ac.kr/bbs/contract/285/138185/artclView.do"
    assert notices[0].published_at is not None


def test_tukorea_board_adapter_deduplicates_duplicate_links() -> None:
    adapter = TukoreaBoardAdapter(
        SiteConfig(name="tukorea-contract-notices", interval_seconds=300, settings={"board_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do"})
    )
    html = SAMPLE_HTML + '<a href="/bbs/contract/285/138185/artclView.do">★중요★ 비콘 출석 안내</a>'

    notices = adapter.parse_notice_list(html, "https://contract.tukorea.ac.kr/contract/2792/subview.do")

    assert [notice.notice_key for notice in notices] == ["138185", "138184"]
