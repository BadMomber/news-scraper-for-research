import asyncio
from datetime import date
from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from src.taz.models import TazSearchResult
from src.taz.search import _build_absolute_url, _filter_by_date, _parse_date, _parse_results_page, _parse_total_count

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def browser(event_loop):
    """Shared browser instance for all tests in this module."""
    pw = event_loop.run_until_complete(async_playwright().start())
    br = event_loop.run_until_complete(pw.chromium.launch(headless=True))
    yield br
    event_loop.run_until_complete(br.close())
    event_loop.run_until_complete(pw.stop())


@pytest.fixture
def page(browser, event_loop):
    """Fresh page for each test."""
    ctx = event_loop.run_until_complete(browser.new_context())
    pg = event_loop.run_until_complete(ctx.new_page())
    yield pg
    event_loop.run_until_complete(ctx.close())


def run(coro, loop):
    """Helper to run async code in sync tests."""
    return loop.run_until_complete(coro)


class TestParseResultsPage:
    def test_extracts_title_url_date(self, page, event_loop):
        fixture_url = (FIXTURES / "taz_search_results.html").as_uri()
        run(page.goto(fixture_url), event_loop)
        results = run(_parse_results_page(page), event_loop)

        assert len(results) == 3

        assert results[0].title == "Grok und die Folgen für die Demokratie"
        assert results[0].url == "https://taz.de/Grok-und-die-Folgen/!6012345/"
        assert results[0].date == date(2026, 1, 15)

        assert results[1].title == "KI-Skandal weitet sich aus"
        assert results[1].date == date(2025, 12, 3)

        assert results[2].title == "Künstliche Intelligenz im Wandel"
        assert results[2].date == date(2025, 8, 22)

    def test_empty_page_returns_empty_list(self, page, event_loop):
        fixture_url = (FIXTURES / "taz_search_empty.html").as_uri()
        run(page.goto(fixture_url), event_loop)
        results = run(_parse_results_page(page), event_loop)

        assert results == []

    def test_handles_umlauts_in_title(self, page, event_loop):
        fixture_url = (FIXTURES / "taz_search_results.html").as_uri()
        run(page.goto(fixture_url), event_loop)
        results = run(_parse_results_page(page), event_loop)

        assert "Künstliche Intelligenz" in results[2].title


class TestParseTotalCount:
    def test_extracts_count(self, page, event_loop):
        fixture_url = (FIXTURES / "taz_search_results.html").as_uri()
        run(page.goto(fixture_url), event_loop)
        total = run(_parse_total_count(page), event_loop)

        assert total == 3

    def test_returns_none_for_no_count(self, page, event_loop):
        fixture_url = (FIXTURES / "taz_search_empty.html").as_uri()
        run(page.goto(fixture_url), event_loop)
        total = run(_parse_total_count(page), event_loop)

        assert total is None


class TestParseDate:
    def test_single_digit_day_and_month(self):
        assert _parse_date("3.1.2026") == date(2026, 1, 3)

    def test_double_digit_day_and_month(self):
        assert _parse_date("15.12.2025") == date(2025, 12, 15)

    def test_mixed_digits(self):
        assert _parse_date("1.10.2025") == date(2025, 10, 1)

    def test_invalid_date_returns_none(self):
        assert _parse_date("32.13.2025") is None

    def test_non_date_string_returns_none(self):
        assert _parse_date("Von Max Mustermann") is None

    def test_empty_string_returns_none(self):
        assert _parse_date("") is None


class TestBuildAbsoluteUrl:
    def test_relative_url(self):
        url = _build_absolute_url("/Grok-Skandal/!6012345&s=Grok%2BHitler/")
        assert url == "https://taz.de/Grok-Skandal/!6012345/"

    def test_strips_search_param(self):
        url = _build_absolute_url("/Artikel/!6099999&s=KI%2BEU/")
        assert "&s=" not in url

    def test_already_absolute(self):
        url = _build_absolute_url("https://taz.de/Artikel/!6099999/")
        assert url == "https://taz.de/Artikel/!6099999/"


class TestFilterByDate:
    def test_filters_out_of_range(self):
        results = [
            TazSearchResult("A", "https://taz.de/a", date(2025, 7, 1)),   # before range
            TazSearchResult("B", "https://taz.de/b", date(2025, 8, 1)),   # in range
            TazSearchResult("C", "https://taz.de/c", date(2026, 1, 15)),  # in range
            TazSearchResult("D", "https://taz.de/d", date(2026, 3, 1)),   # after range
        ]
        filtered = _filter_by_date(results, date(2025, 7, 8), date(2026, 2, 8))

        assert len(filtered) == 2
        assert filtered[0].title == "B"
        assert filtered[1].title == "C"

    def test_inclusive_boundaries(self):
        results = [
            TazSearchResult("Start", "https://taz.de/s", date(2025, 7, 8)),
            TazSearchResult("End", "https://taz.de/e", date(2026, 2, 8)),
        ]
        filtered = _filter_by_date(results, date(2025, 7, 8), date(2026, 2, 8))

        assert len(filtered) == 2

    def test_empty_list(self):
        assert _filter_by_date([], date(2025, 1, 1), date(2026, 1, 1)) == []
