import asyncio
import logging
from datetime import date
from urllib.parse import quote

from playwright.async_api import Browser, Page

from .models import ZeitSearchResult

logger = logging.getLogger(__name__)

BASE_URL = "https://www.zeit.de"
RATE_LIMIT_SECONDS = 2.0
MAX_RETRIES = 3
BACKOFF_SECONDS = [5, 15, 45]


async def search(
    browser: Browser,
    keyword_pair: list[str],
    date_start: date,
    date_end: date,
) -> list[ZeitSearchResult]:
    """Search zeit.de for a keyword pair and return date-filtered results."""
    query = " ".join(keyword_pair)
    encoded_query = quote(query, safe="")

    logger.info("Suche '%s' auf zeit.de", query)

    context = await browser.new_context()
    page = await context.new_page()
    all_results: list[ZeitSearchResult] = []

    try:
        search_url = f"{BASE_URL}/suche/index?q={encoded_query}&sort=publishedDate&type=article"
        await _navigate_with_retry(page, search_url)
        await _dismiss_cookie_banner(page)

        results = await _parse_results_page(page)
        all_results.extend(results)

        # Pagination: p=2, p=3, ...
        page_num = 2
        while results:
            if _should_stop_pagination(results, date_start):
                logger.info(
                    "Suche '%s': Stoppe Pagination auf Seite %d (Ergebnisse vor Zeitraum)",
                    query, page_num - 1,
                )
                break

            await asyncio.sleep(RATE_LIMIT_SECONDS)
            paginated_url = f"{search_url}&p={page_num}"
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


def _should_stop_pagination(results: list[ZeitSearchResult], date_start: date) -> bool:
    """Stop if the oldest result on the page is before the date range."""
    if not results:
        return True
    oldest = min(r.date for r in results)
    return oldest < date_start


async def _dismiss_cookie_banner(page: Page) -> None:
    """Dismiss zeit.de cookie consent banner if present."""
    try:
        for sel in [
            "[data-testid='uc-accept-all-button']",
            "button:has-text('Akzeptieren')",
            "button:has-text('Accept')",
        ]:
            btn = await page.query_selector(sel)
            if btn:
                await btn.click()
                await page.wait_for_timeout(500)
                logger.info("Cookie-Banner weggeklickt")
                break
    except Exception:
        pass


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


async def _parse_results_page(page: Page) -> list[ZeitSearchResult]:
    """Extract search results from zeit.de search page.

    zeit.de structure:
        <article>
          <a href="https://www.zeit.de/path/to/article">
            <h3>
              <span>Topline</span>
              <span>Headline</span>
            </h3>
            <p>Teaser</p>
            <time datetime="2026-01-10T11:43:00+01:00">10. Januar 2026</time>
          </a>
        </article>
    """
    results: list[ZeitSearchResult] = []

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
        # Clean up title: remove extra whitespace from span nesting
        title = " ".join(title.split())
        if not title:
            continue

        # Date from <time datetime="...">
        time_el = await article.query_selector("time[datetime]")
        if time_el is None:
            logger.warning("Kein Datum gefunden für '%s'", title[:60])
            continue

        datetime_str = await time_el.get_attribute("datetime")
        article_date = _parse_iso_date(datetime_str)
        if article_date is None:
            logger.warning("Ungültiges Datum '%s' für '%s'", datetime_str, title[:60])
            continue

        # Z+ detection from article HTML
        art_html = await article.evaluate("el => el.outerHTML.substring(0, 1500)")
        is_zplus = "zon-teaser-premium" in art_html.lower() or "zplus" in art_html.lower()

        url = href if href.startswith("http") else f"{BASE_URL}{href}"

        results.append(ZeitSearchResult(
            title=title,
            url=url,
            date=article_date,
            is_zplus=is_zplus,
        ))

    return results


def _parse_iso_date(datetime_str: str | None) -> date | None:
    """Parse ISO 8601 datetime string to date."""
    if not datetime_str:
        return None
    try:
        return date.fromisoformat(datetime_str[:10])
    except (ValueError, IndexError):
        return None


def _filter_by_date(
    results: list[ZeitSearchResult],
    date_start: date,
    date_end: date,
) -> list[ZeitSearchResult]:
    """Filter results to only include those within the date range (inclusive)."""
    return [r for r in results if date_start <= r.date <= date_end]
