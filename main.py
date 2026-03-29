import asyncio
import logging

from playwright.async_api import async_playwright

from src.config import load_config
from src.dedup import deduplicate, export_csv, to_articles
from src.heise import scrape_articles as heise_scrape
from src.heise import search as heise_search
from src.taz import scrape_articles as taz_scrape
from src.taz import search as taz_search
from src.verify import print_report, verify_csv
from src.zeit import scrape_articles as zeit_scrape
from src.zeit import search as zeit_search

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def _search_and_scrape(browser, site_name, search_fn, scrape_fn, pairs, config, search_offset):
    """Search and scrape a single site for all keyword pairs."""
    all_articles = []
    total_searches = len(pairs) * 3  # 3 sites

    for i, pair in enumerate(pairs):
        search_num = search_offset + i + 1
        query = "+".join(pair)
        logger.info("Suche %d/%d: %s — %s", search_num, total_searches, site_name, query)

        results = await search_fn(
            browser, pair, config.date_start, config.date_end,
        )
        if results:
            articles = await scrape_fn(browser, results, pair)
            all_articles.extend(articles)
            logger.info(
                "Suche %d/%d: %s — %s — %d Treffer, %d Artikel gescrapt",
                search_num, total_searches, site_name, query,
                len(results), len(articles),
            )
        else:
            logger.info(
                "Suche %d/%d: %s — %s — 0 Treffer",
                search_num, total_searches, site_name, query,
            )
        await asyncio.sleep(3)

    logger.info("%s abgeschlossen: %d Artikel", site_name, len(all_articles))
    return all_articles


async def run():
    config = load_config()
    pairs = config.all_keyword_pairs
    total = len(pairs) * 3

    logger.info(
        "%d Keyword-Paare × 3 Seiten = %d Suchen, Zeitraum %s – %s",
        len(pairs), total, config.date_start, config.date_end,
    )

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            taz_articles = await _search_and_scrape(
                browser, "taz.de", taz_search, taz_scrape, pairs, config, 0,
            )
            heise_articles = await _search_and_scrape(
                browser, "heise.de", heise_search, heise_scrape, pairs, config, len(pairs),
            )
            zeit_articles = await _search_and_scrape(
                browser, "zeit.de", zeit_search, zeit_scrape, pairs, config, len(pairs) * 2,
            )
        finally:
            await browser.close()

    # --- Deduplizierung & CSV-Export ---
    all_articles = to_articles(taz_articles, heise_articles, zeit_articles)
    unique = deduplicate(all_articles)
    csv_path = export_csv(unique)

    # Summary
    paywall_count = sum(1 for a in unique if a.paywall)
    print(f"\n{'='*70}")
    print(f"Ergebnis: {len(unique)} eindeutige Artikel ({paywall_count} mit Paywall)")
    print(f"  taz.de:   {len(taz_articles)} Artikel")
    print(f"  heise.de: {len(heise_articles)} Artikel")
    print(f"  zeit.de:  {len(zeit_articles)} Artikel")
    print(f"  Vor Dedup: {len(all_articles)} | Nach Dedup: {len(unique)}")
    print(f"  CSV: {csv_path}")
    print(f"{'='*70}")

    # --- Verifikation ---
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            verification = await verify_csv(browser, csv_path)
            print_report(verification)
        finally:
            await browser.close()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
