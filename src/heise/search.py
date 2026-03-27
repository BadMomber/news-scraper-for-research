import asyncio
import logging
import re
from datetime import date
from urllib.parse import quote

from playwright.async_api import Browser, Page

from .models import HeiseSearchResult

logger = logging.getLogger(__name__)

BASE_URL = "https://www.heise.de"
RATE_LIMIT_SECONDS = 2.0
MAX_RETRIES = 3
BACKOFF_SECONDS = [5, 15, 45]


async def search(
    browser: Browser,
    keyword_pair: list[str],
    date_start: date,
    date_end: date,
) -> list[HeiseSearchResult]:
    """Search heise.de for a keyword pair and return date-filtered results."""
    query = " ".join(keyword_pair)
    encoded_query = quote(query, safe="")

    logger.info("Suche '%s' auf heise.de", query)

    context = await browser.new_context()
    page = await context.new_page()
    all_results: list[HeiseSearchResult] = []

    try:
        # First page
        search_url = f"{BASE_URL}/suche/?q={encoded_query}&sort_by=date"
        await _navigate_with_retry(page, search_url)
        await _dismiss_cookie_banner(page)

        results = await _parse_results_page(page)
        all_results.extend(results)

        total = await _parse_total_count(page)
        if total is not None:
            logger.info("Suche '%s': %d Treffer gesamt", query, total)

        # Pagination: p=2, p=3, ...
        page_num = 2
        while results:
            # Early termination: if oldest result on page is before date range
            if _should_stop_pagination(results, date_start):
                logger.info(
                    "Suche '%s': Stoppe Pagination auf Seite %d (Ergebnisse vor Zeitraum)",
                    query, page_num - 1,
                )
                break

            await asyncio.sleep(RATE_LIMIT_SECONDS)
            paginated_url = f"{BASE_URL}/suche/?q={encoded_query}&sort_by=date&p={page_num}"
            await _navigate_with_retry(page, paginated_url)
            results = await _parse_results_page(page)
            all_results.extend(results)

            logger.info(
                "Suche '%s': Seite %d, %d Treffer auf dieser Seite",
                query, page_num, len(results),
            )
            page_num += 1

        filtered = _filter_by_date(all_results, date_start, date_end)
        logger.info(
            "Suche '%s': %d Treffer nach Datumsfilter (von %d gesamt)",
            query, len(filtered), len(all_results),
        )
        return filtered

    finally:
        await context.close()


def _should_stop_pagination(results: list[HeiseSearchResult], date_start: date) -> bool:
    """Stop pagination if the oldest result on the page is before the date range.

    Results are sorted newest-first (sort_by=date), so the last result
    on the page is the oldest. If it's before date_start, there's no
    point in fetching more pages.
    """
    if not results:
        return True
    oldest = min(r.date for r in results)
    return oldest < date_start


async def _dismiss_cookie_banner(page: Page) -> None:
    """Dismiss heise.de cookie consent banner if present."""
    try:
        agree_btn = await page.query_selector("button:has-text('Agree')")
        if agree_btn is None:
            agree_btn = await page.query_selector("button:has-text('Zustimmen')")
        if agree_btn:
            await agree_btn.click()
            await page.wait_for_timeout(500)
            logger.info("Cookie-Banner weggeklickt")
    except Exception:
        pass


async def _navigate_with_retry(page: Page, url: str) -> None:
    """Navigate to URL with retry and exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
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


async def _parse_results_page(page: Page) -> list[HeiseSearchResult]:
    """Extract search results from the current heise.de search page.

    heise.de structure:
        <article data-content-id="...">
          <a href="/news/Article-Title-12345.html">
            <img ...>
            <div>
              <h2>Article Title</h2>
              <p>Teaser</p>
              <time datetime="2026-01-10T11:43:00.000Z">10.01.2026</time>
            </div>
          </a>
        </article>
    """
    results: list[HeiseSearchResult] = []

    articles = await page.query_selector_all("article")

    for article in articles:
        link_el = await article.query_selector("a[href]")
        if link_el is None:
            continue

        href = await link_el.get_attribute("href")
        if not href:
            continue

        # Title from heading
        title_el = await article.query_selector("h2, h3, h4")
        if title_el is None:
            continue
        title = (await title_el.inner_text()).strip()
        if not title:
            continue

        # Date from <time datetime="...">
        time_el = await article.query_selector("time[datetime]")
        if time_el is None:
            logger.warning("Kein Datum gefunden für '%s'", title)
            continue

        datetime_str = await time_el.get_attribute("datetime")
        article_date = _parse_iso_date(datetime_str)
        if article_date is None:
            logger.warning("Ungültiges Datum '%s' für '%s'", datetime_str, title)
            continue

        url = _build_absolute_url(href)
        is_heise_plus = "/select/" in href

        results.append(HeiseSearchResult(
            title=title,
            url=url,
            date=article_date,
            is_heise_plus=is_heise_plus,
        ))

    return results


async def _parse_total_count(page: Page) -> int | None:
    """Extract total result count from page text like '15.365 Ergebnisse'."""
    try:
        body_text = await page.inner_text("body")
        match = re.search(r"([\d.]+)\s*Ergebnis", body_text)
        if match:
            # Remove thousand separators (dots)
            count_str = match.group(1).replace(".", "")
            return int(count_str)
    except Exception:
        pass
    return None


def _build_absolute_url(href: str) -> str:
    """Convert relative heise.de href to absolute URL."""
    if href.startswith("/"):
        return f"{BASE_URL}{href}"
    if href.startswith("http"):
        return href
    return f"{BASE_URL}/{href}"


def _parse_iso_date(datetime_str: str | None) -> date | None:
    """Parse ISO 8601 datetime string to date."""
    if not datetime_str:
        return None
    try:
        # Handle "2026-01-10T11:43:00.000Z" format
        return date.fromisoformat(datetime_str[:10])
    except (ValueError, IndexError):
        return None


def _filter_by_date(
    results: list[HeiseSearchResult],
    date_start: date,
    date_end: date,
) -> list[HeiseSearchResult]:
    """Filter results to only include those within the date range (inclusive)."""
    return [r for r in results if date_start <= r.date <= date_end]
