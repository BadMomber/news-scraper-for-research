import asyncio
import logging

from playwright.async_api import async_playwright

from src.config import load_config
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
            all_taz_results = []
            for pair in pairs:
                results = await taz_search(
                    browser, pair, config.date_start, config.date_end,
                )
                all_taz_results.extend(results)
                await asyncio.sleep(3)

            logger.info("taz.de: %d Treffer gesamt", len(all_taz_results))

            print(f"\n{'='*70}")
            print(f"taz.de — {len(all_taz_results)} Treffer im Zeitraum")
            print(f"{'='*70}")
            for r in all_taz_results:
                print(f"  {r.date}  {r.title}")
                print(f"           {r.url}")

        finally:
            await browser.close()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
