import asyncio
from datetime import date
from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from src.zeit.models import ZeitSearchResult
from src.zeit.search import (
    _filter_by_date,
    _parse_iso_date,
    _parse_results_page,
    _should_stop_pagination,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def browser(event_loop):
    pw = event_loop.run_until_complete(async_playwright().start())
    br = event_loop.run_until_complete(pw.chromium.launch(headless=True))
    yield br
    event_loop.run_until_complete(br.close())
    event_loop.run_until_complete(pw.stop())


@pytest.fixture
def page(browser, event_loop):
    ctx = event_loop.run_until_complete(browser.new_context())
    pg = event_loop.run_until_complete(ctx.new_page())
    yield pg
    event_loop.run_until_complete(ctx.close())


def run(coro, loop):
    return loop.run_until_complete(coro)


class TestParseResultsPage:
    def test_extracts_title_url_date(self, page, event_loop):
        url = (FIXTURES / "zeit_search_results.html").as_uri()
        run(page.goto(url), event_loop)
        results = run(_parse_results_page(page), event_loop)

        assert len(results) == 3

        assert results[0].title == "KI-Slop Wenn alles fake ist"
        assert results[0].url == "https://www.zeit.de/digital/2025-10/ki-slop-internet"
        assert results[0].date == date(2025, 10, 11)
        assert results[0].is_zplus is False

    def test_zplus_detection(self, page, event_loop):
        url = (FIXTURES / "zeit_search_results.html").as_uri()
        run(page.goto(url), event_loop)
        results = run(_parse_results_page(page), event_loop)

        assert results[1].is_zplus is True
        assert results[0].is_zplus is False
        assert results[2].is_zplus is False

    def test_empty_page(self, page, event_loop):
        url = (FIXTURES / "zeit_search_empty.html").as_uri()
        run(page.goto(url), event_loop)
        results = run(_parse_results_page(page), event_loop)

        assert results == []


class TestParseIsoDate:
    def test_with_timezone(self):
        assert _parse_iso_date("2025-10-11T12:06:30+02:00") == date(2025, 10, 11)

    def test_date_only(self):
        assert _parse_iso_date("2025-09-03") == date(2025, 9, 3)

    def test_none(self):
        assert _parse_iso_date(None) is None

    def test_invalid(self):
        assert _parse_iso_date("invalid") is None


class TestShouldStopPagination:
    def test_stops_when_oldest_before_range(self):
        results = [
            ZeitSearchResult("A", "u", date(2025, 8, 1), False),
            ZeitSearchResult("B", "u", date(2025, 7, 1), False),
        ]
        assert _should_stop_pagination(results, date(2025, 7, 8)) is True

    def test_continues_when_all_in_range(self):
        results = [
            ZeitSearchResult("A", "u", date(2025, 10, 1), False),
            ZeitSearchResult("B", "u", date(2025, 9, 1), False),
        ]
        assert _should_stop_pagination(results, date(2025, 7, 8)) is False

    def test_stops_on_empty(self):
        assert _should_stop_pagination([], date(2025, 7, 8)) is True


class TestFilterByDate:
    def test_filters_out_of_range(self):
        results = [
            ZeitSearchResult("A", "u", date(2025, 7, 1), False),
            ZeitSearchResult("B", "u", date(2025, 8, 1), False),
            ZeitSearchResult("C", "u", date(2026, 3, 1), False),
        ]
        filtered = _filter_by_date(results, date(2025, 7, 8), date(2026, 2, 8))
        assert len(filtered) == 1
        assert filtered[0].title == "B"

    def test_inclusive_boundaries(self):
        results = [
            ZeitSearchResult("Start", "u", date(2025, 7, 8), False),
            ZeitSearchResult("End", "u", date(2026, 2, 8), False),
        ]
        filtered = _filter_by_date(results, date(2025, 7, 8), date(2026, 2, 8))
        assert len(filtered) == 2
