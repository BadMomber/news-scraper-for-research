import asyncio
import logging

from playwright.async_api import async_playwright

from src.config import load_config
from src.taz import scrape_articles as taz_scrape
from src.taz import search as taz_search

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

            logger.info("taz.de: %d Artikel gesamt", len(all_taz_articles))

            print(f"\n{'='*70}")
            print(f"taz.de — {len(all_taz_articles)} Artikel")
            print(f"{'='*70}")
            for a in all_taz_articles:
                print(f"  {a.date}  {a.title}")
                print(f"           Autor: {a.author or '(kein Autor)'}")
                print(f"           {a.char_count} Zeichen | Suche: {a.search_terms}")
                print(f"           {a.url}")

        finally:
            await browser.close()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
