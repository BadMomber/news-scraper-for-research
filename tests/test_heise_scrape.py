import asyncio
from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from src.heise.scrape import _extract_author, _extract_body_text

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
        url = (FIXTURES / "heise_article.html").as_uri()
        run(page.goto(url), event_loop)
        author = run(_extract_author(page), event_loop)

        assert author == "Niklas Jan Engelking"

    def test_no_author_heise_plus(self, page, event_loop):
        url = (FIXTURES / "heise_article_plus.html").as_uri()
        run(page.goto(url), event_loop)
        author = run(_extract_author(page), event_loop)

        assert author == ""

    def test_fallback_to_meta(self, page, event_loop):
        """When no author link exists but meta tag has content."""
        url = (FIXTURES / "heise_article.html").as_uri()
        run(page.goto(url), event_loop)
        # meta[name=author] is set in fixture, but author link takes priority
        author = run(_extract_author(page), event_loop)
        assert author == "Niklas Jan Engelking"


class TestExtractBodyText:
    def test_extracts_paragraphs(self, page, event_loop):
        url = (FIXTURES / "heise_article.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert "britischen Regierung" in text
        assert "Technologieministerin" in text
        assert "\n" in text

    def test_heise_plus_teaser_only(self, page, event_loop):
        url = (FIXTURES / "heise_article_plus.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert "Sprachmodelle" in text
        assert len(text) > 0

    def test_char_count(self, page, event_loop):
        url = (FIXTURES / "heise_article.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert len(text) > 100

    def test_empty_article(self, page, event_loop):
        url = (FIXTURES / "heise_search_empty.html").as_uri()
        run(page.goto(url), event_loop)
        text = run(_extract_body_text(page), event_loop)

        assert text == ""
