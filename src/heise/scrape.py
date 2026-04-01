import asyncio
import logging

from playwright.async_api import Browser, Page

from .models import HeiseArticle, HeiseSearchResult
from .search import _dismiss_cookie_banner, RATE_LIMIT_SECONDS, MAX_RETRIES, BACKOFF_SECONDS

logger = logging.getLogger(__name__)


async def scrape_articles(
    browser: Browser,
    results: list[HeiseSearchResult],
    keyword_pair: list[str],
) -> list[HeiseArticle]:
    """Scrape article details for each heise.de search result."""
    search_terms = "+".join(keyword_pair)
    articles: list[HeiseArticle] = []

    context = await browser.new_context()
    page = await context.new_page()
    cookie_dismissed = False

    try:
        for i, result in enumerate(results):
            logger.info("Scrape %d/%d: %s", i + 1, len(results), result.url)

            try:
                await _navigate_with_retry(page, result.url)
            except Exception as e:
                logger.error("Überspringe Artikel '%s': %s", result.title, e)
                continue

            if not cookie_dismissed:
                await _dismiss_cookie_banner(page)
                cookie_dismissed = True

            author = await _extract_author(page)
            body_text = await _extract_body_text(page)
            char_count = len(body_text)

            articles.append(HeiseArticle(
                date=result.date,
                url=result.url,
                title=result.title,
                author=author,
                char_count=char_count,
                search_terms=search_terms,
                is_heise_plus=result.is_heise_plus,
                body_text=body_text,
            ))

            if i < len(results) - 1:
                await asyncio.sleep(RATE_LIMIT_SECONDS)

    finally:
        await context.close()

    logger.info(
        "Scrape '%s': %d/%d Artikel erfolgreich",
        search_terms, len(articles), len(results),
    )
    return articles


async def _navigate_with_retry(page: Page, url: str) -> None:
    """Navigate to URL with retry and exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                logger.error("Navigation fehlgeschlagen nach %d Versuchen: %s", MAX_RETRIES, url)
                raise
            backoff = BACKOFF_SECONDS[attempt]
            logger.warning(
                "Navigation fehlgeschlagen (Versuch %d/%d), warte %ds: %s",
                attempt + 1, MAX_RETRIES, backoff, e,
            )
            await asyncio.sleep(backoff)


async def _extract_author(page: Page) -> str:
    """Extract author name(s) from heise.de article page.

    Primary: <a href="/autor/Name-12345"> elements
    Fallback: <meta name="author"> tag
    """
    author_links = await page.query_selector_all("a[href*='/autor/']")

    seen = set()
    authors = []
    for link in author_links:
        name = (await link.inner_text()).strip()
        if name and name not in seen:
            seen.add(name)
            authors.append(name)

    if authors:
        return ", ".join(authors)

    # Fallback: meta tag
    meta = await page.query_selector("meta[name='author']")
    if meta:
        content = await meta.get_attribute("content")
        if content and content.strip():
            return content.strip()

    return ""


async def _extract_body_text(page: Page) -> str:
    """Extract article body text with Markdown-style headings from heise.de.

    Uses <p> and subheading elements within the article content area.
    heise.de marks article subheadings with class "subheading" inside
    div.article-content. Subheadings are prefixed with "## " or "### "
    in the output. For heise+ articles, this returns only the visible
    teaser text. If no text is found (some heise+ articles have no
    visible paragraphs), falls back to the meta description.
    """
    elements = await page.query_selector_all(
        "article div.article-content > p,"
        " article div.article-content > .subheading,"
        " article > p"
    )

    texts = []
    for el in elements:
        tag = await el.evaluate("el => el.tagName")
        text = (await el.inner_text()).strip()
        if not text:
            continue
        if tag == "H2":
            texts.append(f"\n## {text}")
        elif tag == "H3":
            texts.append(f"\n### {text}")
        else:
            texts.append(text)

    if texts:
        return "\n".join(texts).strip()

    # Fallback for heise+ articles with no visible paragraphs
    meta = await page.query_selector("meta[name='description']")
    if meta:
        content = await meta.get_attribute("content")
        if content and content.strip():
            return content.strip()

    return ""
