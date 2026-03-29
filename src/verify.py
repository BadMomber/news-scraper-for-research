import asyncio
import csv
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from playwright.async_api import Browser, Page

logger = logging.getLogger(__name__)

RATE_LIMIT_SECONDS = 2.0
MAX_RETRIES = 2
BACKOFF_SECONDS = [5, 15]


@dataclass
class VerificationResult:
    url: str
    title_csv: str
    date_csv: str
    status: str  # "bestanden", "link_fehler", "titel_abweichung", "datum_abweichung"
    details: str = ""


async def verify_csv(browser: Browser, csv_path: Path) -> list[VerificationResult]:
    """Verify all articles in the CSV file."""
    articles = _read_csv(csv_path)
    logger.info("Verifikation: %d Artikel zu prüfen", len(articles))

    results: list[VerificationResult] = []

    for i, article in enumerate(articles):
        logger.info("Verifiziere %d/%d: %s", i + 1, len(articles), article["Link"])

        result = await _verify_article(browser, article)
        results.append(result)

        if i < len(articles) - 1:
            await asyncio.sleep(RATE_LIMIT_SECONDS)

    return results


def print_report(results: list[VerificationResult]) -> None:
    """Print verification report to console."""
    passed = [r for r in results if r.status == "bestanden"]
    link_errors = [r for r in results if r.status == "link_fehler"]
    title_mismatches = [r for r in results if r.status == "titel_abweichung"]
    date_mismatches = [r for r in results if r.status == "datum_abweichung"]

    print(f"\n{'='*70}")
    print(f"VERIFIKATIONSBERICHT")
    print(f"{'='*70}")
    print(f"  Geprüft:             {len(results)} Artikel")
    print(f"  Bestanden:           {len(passed)}")
    print(f"  Link nicht erreichbar: {len(link_errors)}")
    print(f"  Titel-Abweichung:    {len(title_mismatches)}")
    print(f"  Datum-Abweichung:    {len(date_mismatches)}")

    if link_errors:
        print(f"\n--- Link-Fehler ({len(link_errors)}) ---")
        for r in link_errors:
            print(f"  {r.url}")
            print(f"    {r.details}")

    if title_mismatches:
        print(f"\n--- Titel-Abweichungen ({len(title_mismatches)}) ---")
        for r in title_mismatches:
            print(f"  {r.url}")
            print(f"    {r.details}")

    if date_mismatches:
        print(f"\n--- Datum-Abweichungen ({len(date_mismatches)}) ---")
        for r in date_mismatches:
            print(f"  {r.url}")
            print(f"    {r.details}")

    print(f"{'='*70}")


def _read_csv(csv_path: Path) -> list[dict[str, str]]:
    """Read CSV and return list of article dicts."""
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


async def _verify_article(browser: Browser, article: dict[str, str]) -> VerificationResult:
    """Verify a single article: check link, compare title and date."""
    url = article["Link"]
    title_csv = article["Titel"]
    date_csv = article["Date"]

    context = await browser.new_context()
    page = await context.new_page()

    try:
        # Load the page
        try:
            await _navigate_with_retry(page, url)
        except Exception as e:
            return VerificationResult(
                url=url, title_csv=title_csv, date_csv=date_csv,
                status="link_fehler",
                details=str(e)[:200],
            )

        # Dismiss cookie banners
        await _dismiss_cookies(page)

        # Extract title from page
        title_page = await _extract_title(page, url)

        # Extract date from page
        date_page = await _extract_date(page, url)

        # Compare title
        if title_page and not _titles_match(title_csv, title_page):
            return VerificationResult(
                url=url, title_csv=title_csv, date_csv=date_csv,
                status="titel_abweichung",
                details=f"CSV: '{title_csv[:60]}' vs Seite: '{title_page[:60]}'",
            )

        # Compare date
        if date_page and date_csv != date_page:
            return VerificationResult(
                url=url, title_csv=title_csv, date_csv=date_csv,
                status="datum_abweichung",
                details=f"CSV: {date_csv} vs Seite: {date_page}",
            )

        return VerificationResult(
            url=url, title_csv=title_csv, date_csv=date_csv,
            status="bestanden",
        )

    finally:
        await context.close()


async def _navigate_with_retry(page: Page, url: str) -> None:
    """Navigate with retry."""
    for attempt in range(MAX_RETRIES):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(BACKOFF_SECONDS[attempt])


async def _dismiss_cookies(page: Page) -> None:
    """Try to dismiss cookie banners."""
    try:
        for sel in [
            "button:has-text('Agree')",
            "[data-testid='uc-accept-all-button']",
            "button:has-text('Akzeptieren')",
        ]:
            btn = await page.query_selector(sel)
            if btn:
                await btn.click()
                await page.wait_for_timeout(300)
                break
    except Exception:
        pass


async def _extract_title(page: Page, url: str) -> str:
    """Extract article title from page."""
    # Site-specific selectors
    if "taz.de" in url:
        el = await page.query_selector("article h1, article h2, h1 span.headline")
        if el:
            return " ".join((await el.inner_text()).strip().split())
    elif "heise.de" in url:
        el = await page.query_selector("article h1, h1")
        if el:
            return (await el.inner_text()).strip()
    elif "zeit.de" in url:
        el = await page.query_selector("article h1, h1")
        if el:
            return " ".join((await el.inner_text()).strip().split())

    # Fallback: any h1
    el = await page.query_selector("h1")
    if el:
        return (await el.inner_text()).strip()
    return ""


async def _extract_date(page: Page, url: str) -> str:
    """Extract article date from page as ISO string."""
    time_el = await page.query_selector("time[datetime]")
    if time_el:
        dt = await time_el.get_attribute("datetime")
        if dt and len(dt) >= 10:
            return dt[:10]
    return ""


def _titles_match(csv_title: str, page_title: str) -> bool:
    """Compare titles with tolerance for whitespace differences."""
    normalized_csv = " ".join(csv_title.split()).lower()
    normalized_page = " ".join(page_title.split()).lower()
    # Check if one contains the other (page titles often have prefixes/suffixes)
    return normalized_csv in normalized_page or normalized_page in normalized_csv
