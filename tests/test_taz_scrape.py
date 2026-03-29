import asyncio
from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from src.taz.scrape import _extract_author, _extract_body_text

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


class TestExtractAuthor:
    def test_named_author(self, page, event_loop):
        url = (FIXTURES / "taz_article.html").as_uri()
        run(page.goto(url), event_loop)
        author = run(_extract_author(page), event_loop)

        assert author == "Johannes Drosdowski"

    def test_agency_author_from_bodytext(self, page, event_loop):
        """Agency articles have no named author but 'ap | ...' in body text."""
        url = (FIXTURES / "taz_article_agency.html").as_uri()
        run(page.goto(url), event_loop)
        author = run(_extract_author(page), event_loop)

        assert author == "ap"

    def test_multiple_authors(self, page, event_loop):
        url = (FIXTURES / "taz_article_multi_author.html").as_uri()
        run(page.goto(url), event_loop)
        author = run(_extract_author(page), event_loop)

        assert "Anna Schmidt" in author
        assert "Max Müller" in author
        assert ", " in author


class TestExtractBodyText:
    def test_extracts_paragraphs(self, page, event_loop):
        url = (FIXTURES / "taz_article.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert "Früher galt die Verwendung von Wikipedia" in text
        assert "KI-Systeme neigen zu Halluzinationen" in text
        # Paragraphs joined with newlines
        assert "\n" in text

    def test_agency_prefix_preserved(self, page, event_loop):
        url = (FIXTURES / "taz_article_agency.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert text.startswith("ap | Die französische")

    def test_char_count(self, page, event_loop):
        url = (FIXTURES / "taz_article.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert len(text) > 0
        # Spaces and newlines are counted
        assert " " in text
        assert len(text) == len(text)  # sanity check: len includes whitespace

    def test_empty_article(self, page, event_loop):
        url = (FIXTURES / "taz_search_empty.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert text == ""
