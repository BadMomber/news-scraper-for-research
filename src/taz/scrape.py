import asyncio
import logging

from playwright.async_api import Browser, Page

from .models import TazArticle, TazSearchResult
from .search import _navigate_with_retry, RATE_LIMIT_SECONDS

logger = logging.getLogger(__name__)


async def scrape_articles(
    browser: Browser,
    results: list[TazSearchResult],
    keyword_pair: list[str],
) -> list[TazArticle]:
    """Scrape article details for each search result."""
    search_terms = "+".join(keyword_pair)
    articles: list[TazArticle] = []

    context = await browser.new_context()
    page = await context.new_page()

    try:
        for i, result in enumerate(results):
            logger.info(
                "Scrape %d/%d: %s", i + 1, len(results), result.url,
            )

            try:
                await _navigate_with_retry(page, result.url)
            except Exception as e:
                logger.error("Überspringe Artikel '%s': %s", result.title, e)
                continue

            author = await _extract_author(page)
            body_text = await _extract_body_text(page)
            char_count = len(body_text)

            articles.append(TazArticle(
                date=result.date,
                url=result.url,
                title=result.title,
                author=author,
                char_count=char_count,
                search_terms=search_terms,
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


async def _extract_author(page: Page) -> str:
    """Extract author name(s) from the article page.

    taz.de structure:
        <div class="author-container ...">  (in article header area)
          <div class="author-name-wrapper ...">
            <a href="/Author-Name/!aID/">Author Name</a>
          </div>
        </div>

    There may be multiple author-container elements on the page (article
    authors + comment authors). We only want the first one(s) that appear
    before the article body.
    """
    # Select author links from the first author-container in the article
    article_el = await page.query_selector("article")
    if article_el is None:
        return ""

    author_links = await article_el.query_selector_all(
        "div.author-name-wrapper a"
    )

    seen = set()
    authors = []
    for link in author_links:
        name = (await link.inner_text()).strip()
        if name and name not in seen:
            seen.add(name)
            authors.append(name)

    if authors:
        return ", ".join(authors)

    # Fallback: extract agency prefix from body text (e.g. "dpa | ..." or "ap | ...")
    return await _extract_agency_author(page)


async def _extract_agency_author(page: Page) -> str:
    """Extract news agency name from body text prefix like 'dpa | ...'."""
    first_p = await page.query_selector("article p.bodytext")
    if first_p is None:
        return ""
    text = (await first_p.inner_text()).strip()
    if " | " in text:
        agency = text.split(" | ", 1)[0].strip()
        if len(agency) <= 10:  # Agency names are short (dpa, ap, afp, rtr)
            return agency
    return ""


async def _extract_body_text(page: Page) -> str:
    """Extract article body text with Markdown-style headings.

    taz.de structure:
        <article>
          <h2 class="typo-r-subhead ...">Subheading</h2>
          <p class="bodytext paragraph typo-bodytext ...">Text</p>
          ...
        </article>

    Subheadings are prefixed with "## " in the output.
    Agency prefixes like "dpa | " or "ap | " remain in the text.
    """
    elements = await page.query_selector_all(
        "article p.bodytext, article h2.typo-r-subhead"
    )

    texts = []
    for el in elements:
        tag = await el.evaluate("el => el.tagName")
        text = (await el.inner_text()).strip()
        if not text:
            continue
        if tag == "H2":
            texts.append(f"\n## {text}")
        else:
            texts.append(text)

    return "\n".join(texts).strip()
