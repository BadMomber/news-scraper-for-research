import asyncio
from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from src.zeit.scrape import _extract_author, _extract_body_text

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
    def test_named_author_from_title_attr(self, page, event_loop):
        """Author name comes from title attribute, not the shortcode."""
        url = (FIXTURES / "zeit_article.html").as_uri()
        run(page.goto(url), event_loop)
        author = run(_extract_author(page), event_loop)

        assert author == "Nina Monecke"

    def test_multiple_authors(self, page, event_loop):
        url = (FIXTURES / "zeit_article_zplus.html").as_uri()
        run(page.goto(url), event_loop)
        author = run(_extract_author(page), event_loop)

        assert "Jakob von Lindern" in author
        assert "Pauline Schinkels" in author
        assert ", " in author

    def test_no_author(self, page, event_loop):
        url = (FIXTURES / "zeit_search_empty.html").as_uri()
        run(page.goto(url), event_loop)
        author = run(_extract_author(page), event_loop)

        assert author == ""


class TestExtractBodyText:
    def test_extracts_paragraphs(self, page, event_loop):
        url = (FIXTURES / "zeit_article.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert "Elon Musk" in text
        assert "kindgerecht" in text
        assert "\n" in text

    def test_zplus_teaser(self, page, event_loop):
        url = (FIXTURES / "zeit_article_zplus.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert "schlauer" in text
        assert len(text) > 0

    def test_char_count(self, page, event_loop):
        url = (FIXTURES / "zeit_article.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert len(text) > 50

    def test_empty_page(self, page, event_loop):
        url = (FIXTURES / "zeit_search_empty.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert text == ""
