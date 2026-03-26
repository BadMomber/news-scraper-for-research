import asyncio
import logging
import re
from datetime import date
from urllib.parse import quote

from playwright.async_api import Browser, Page

from .models import TazSearchResult

logger = logging.getLogger(__name__)

BASE_URL = "https://taz.de"
RATE_LIMIT_SECONDS = 2.0
MAX_RETRIES = 3
BACKOFF_SECONDS = [5, 15, 45]


async def search(
    browser: Browser,
    keyword_pair: list[str],
    date_start: date,
    date_end: date,
) -> list[TazSearchResult]:
    """Search taz.de for a keyword pair and return date-filtered results."""
    query = "+".join(keyword_pair)
    encoded_query = quote(query, safe="")
    base_search_url = f"{BASE_URL}/!s={encoded_query}/"

    logger.info("Suche '%s' auf taz.de", query)

    context = await browser.new_context()
    page = await context.new_page()
    all_results: list[TazSearchResult] = []

    try:
        # First page has no search_page parameter
        await _navigate_with_retry(page, base_search_url)
        results = await _parse_results_page(page)
        all_results.extend(results)

        total = await _parse_total_count(page)
        if total is not None:
            logger.info("Suche '%s': %d Treffer gesamt", query, total)

        # Pagination: search_page=0 is page 2, search_page=1 is page 3, etc.
        page_index = 0
        while results:
            # Stop if we already have all results
            if total is not None and len(all_results) >= total:
                break

            await asyncio.sleep(RATE_LIMIT_SECONDS)
            paginated_url = f"{base_search_url}?search_page={page_index}"
            await _navigate_with_retry(page, paginated_url)
            results = await _parse_results_page(page)
            all_results.extend(results)

            logger.info(
                "Suche '%s': Seite %d, %d Treffer auf dieser Seite",
                query, page_index + 2, len(results),
            )
            page_index += 1

        filtered = _filter_by_date(all_results, date_start, date_end)
        logger.info(
            "Suche '%s': %d Treffer nach Datumsfilter (von %d gesamt)",
            query, len(filtered), len(all_results),
        )
        return filtered

    finally:
        await context.close()


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


async def _parse_results_page(page: Page) -> list[TazSearchResult]:
    """Extract search results from the current page."""
    results: list[TazSearchResult] = []

    # Each result has an h3 with an <a> link, followed by <p> elements
    headings = await page.query_selector_all("h3 > a")

    for link_el in headings:
        href = await link_el.get_attribute("href")
        title = (await link_el.inner_text()).strip()

        if not href or not title:
            continue

        # Build absolute URL, strip search parameter from href
        url = _build_absolute_url(href)

        # Find the parent container and look for date in sibling <p> elements
        h3_el = await link_el.evaluate_handle("el => el.closest('h3')")
        container = await h3_el.evaluate_handle("el => el.parentElement")

        # Get all <p> elements in the container
        p_elements = await container.query_selector_all("p")
        article_date = None
        for p_el in p_elements:
            text = await p_el.inner_text()
            article_date = _parse_date(text.strip())
            if article_date is not None:
                break

        if article_date is None:
            logger.warning("Kein Datum gefunden für '%s' (%s)", title, url)
            continue

        results.append(TazSearchResult(title=title, url=url, date=article_date))

    return results


async def _parse_total_count(page: Page) -> int | None:
    """Extract total result count from 'Suchergebnis 1 bis 20 von N' text."""
    try:
        body_text = await page.inner_text("body")
        match = re.search(r"Suchergebnis\s+\d+\s+bis\s+\d+\s+von\s+(\d+)", body_text)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return None


def _build_absolute_url(href: str) -> str:
    """Convert relative taz.de href to absolute URL, stripping search params."""
    # Remove search parameter from URL (e.g. &s=Grok%2BHitler)
    clean_href = re.sub(r"&s=[^/]*", "", href)
    if clean_href.startswith("/"):
        return f"{BASE_URL}{clean_href}"
    return clean_href


def _parse_date(text: str) -> date | None:
    """Parse date from taz.de format 'D.M.YYYY' or 'DD.MM.YYYY'."""
    match = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$", text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return date(year, month, day)
        except ValueError:
            return None
    return None


def _filter_by_date(
    results: list[TazSearchResult],
    date_start: date,
    date_end: date,
) -> list[TazSearchResult]:
    """Filter results to only include those within the date range (inclusive)."""
    return [r for r in results if date_start <= r.date <= date_end]
