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


async def run():
    config = load_config()
    pairs = config.all_keyword_pairs

    logger.info(
        "%d Keyword-Paare, %d Kategorien, Zeitraum %s – %s",
        len(pairs), len(config.search_terms), config.date_start, config.date_end,
    )

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            # --- taz.de ---
            all_taz_articles = []
            for pair in pairs:
                results = await taz_search(
                    browser, pair, config.date_start, config.date_end,
                )
                if results:
                    articles = await taz_scrape(browser, results, pair)
                    all_taz_articles.extend(articles)
                await asyncio.sleep(3)
            logger.info("taz.de: %d Artikel", len(all_taz_articles))

            # --- heise.de ---
            all_heise_articles = []
            for pair in pairs:
                results = await heise_search(
                    browser, pair, config.date_start, config.date_end,
                )
                if results:
                    articles = await heise_scrape(browser, results, pair)
                    all_heise_articles.extend(articles)
                await asyncio.sleep(3)
            logger.info("heise.de: %d Artikel", len(all_heise_articles))

            # --- zeit.de ---
            all_zeit_articles = []
            for pair in pairs:
                results = await zeit_search(
                    browser, pair, config.date_start, config.date_end,
                )
                if results:
                    articles = await zeit_scrape(browser, results, pair)
                    all_zeit_articles.extend(articles)
                await asyncio.sleep(3)
            logger.info("zeit.de: %d Artikel", len(all_zeit_articles))

        finally:
            await browser.close()

    # --- Deduplizierung & CSV-Export ---
    all_articles = to_articles(all_taz_articles, all_heise_articles, all_zeit_articles)
    unique = deduplicate(all_articles)
    csv_path = export_csv(unique)

    # Summary
    paywall_count = sum(1 for a in unique if a.paywall)
    print(f"\n{'='*70}")
    print(f"Ergebnis: {len(unique)} eindeutige Artikel ({paywall_count} mit Paywall)")
    print(f"  taz.de:   {len(all_taz_articles)} Artikel")
    print(f"  heise.de: {len(all_heise_articles)} Artikel")
    print(f"  zeit.de:  {len(all_zeit_articles)} Artikel")
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
