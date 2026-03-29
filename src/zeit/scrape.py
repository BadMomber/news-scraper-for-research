import asyncio
import logging

from playwright.async_api import Browser, Page

from .models import ZeitArticle, ZeitSearchResult
from .search import _dismiss_cookie_banner, RATE_LIMIT_SECONDS, MAX_RETRIES, BACKOFF_SECONDS

logger = logging.getLogger(__name__)


async def scrape_articles(
    browser: Browser,
    results: list[ZeitSearchResult],
    keyword_pair: list[str],
) -> list[ZeitArticle]:
    """Scrape article details for each zeit.de search result.

    Each article is opened in a fresh browser context to avoid
    triggering the metered paywall (no cookies from previous visits).
    """
    search_terms = "+".join(keyword_pair)
    articles: list[ZeitArticle] = []

    for i, result in enumerate(results):
        logger.info("Scrape %d/%d: %s", i + 1, len(results), result.url)

        # Fresh context per article to avoid metered paywall
        context = await browser.new_context()
        page = await context.new_page()

        try:
            try:
                await _navigate_with_retry(page, result.url)
            except Exception as e:
                logger.error("Überspringe Artikel '%s': %s", result.title, e)
                continue

            await _dismiss_cookie_banner(page)

            author = await _extract_author(page)
            body_text = await _extract_body_text(page)
            char_count = len(body_text)

            articles.append(ZeitArticle(
                date=result.date,
                url=result.url,
                title=result.title,
                author=author,
                char_count=char_count,
                search_terms=search_terms,
                is_zplus=result.is_zplus,
            ))
        finally:
            await context.close()

        if i < len(results) - 1:
            await asyncio.sleep(RATE_LIMIT_SECONDS)

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
    """Extract author name(s) from zeit.de article page.

    zeit.de structure:
        <a href="/autoren/X/Name/index" title="Full Name" rel="author">
          <span itemprop="name">shortname</span>
        </a>

    The title attribute contains the full name, innerText may be a shortcode.
    """
    author_links = await page.query_selector_all("a[href*='/autoren/'][rel='author']")

    if not author_links:
        # Fallback: any link to /autoren/
        author_links = await page.query_selector_all("a[href*='/autoren/']")

    seen = set()
    authors = []
    for link in author_links:
        # Prefer title attribute (full name) over innerText (may be shortcode)
        title_attr = await link.get_attribute("title")
        name = title_attr.strip() if title_attr else (await link.inner_text()).strip()
        if name and name not in seen:
            seen.add(name)
            authors.append(name)

    return ", ".join(authors)


async def _extract_body_text(page: Page) -> str:
    """Extract article body text from zeit.de page.

    Uses all <p> elements within <article>. For Z+ articles,
    this returns only the visible teaser text.
    """
    paragraphs = await page.query_selector_all("article p")

    texts = []
    for p in paragraphs:
        text = await p.inner_text()
        stripped = text.strip()
        if stripped:
            texts.append(stripped)

    return "\n".join(texts)
