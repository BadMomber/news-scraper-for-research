import asyncio
import logging
from pathlib import Path

from playwright.async_api import async_playwright

from src.config import load_config
from src.dedup import Article, IncrementalWriter
from src.fulltext_filter import filter_articles
from src.heise import scrape_articles as heise_scrape
from src.zeit.scrape import create_logged_in_context
from src.heise import search as heise_search
from src.taz import scrape_articles as taz_scrape
from src.taz import search as taz_search
from src.verify import print_report, verify_csv
from src.zeit import scrape_articles as zeit_scrape
from src.zeit import search as zeit_search

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def _search_and_scrape(
    browser, site_name, search_fn, scrape_fn, to_articles_fn,
    pairs, config, search_offset, writer, scrape_kwargs=None,
):
    """Search and scrape a single site for all keyword pairs."""
    site_count = 0
    total_searches = len(pairs) * 3  # 3 sites
    extra = scrape_kwargs or {}

    for i, pair in enumerate(pairs):
        search_num = search_offset + i + 1
        query = "+".join(pair)
        logger.info("Suche %d/%d: %s — %s", search_num, total_searches, site_name, query)

        results = await search_fn(
            browser, pair, config.date_start, config.date_end,
        )
        if results:
            articles = await scrape_fn(browser, results, pair, **extra)
            unified = to_articles_fn(articles)
            writer.add_articles(unified)
            site_count += len(articles)
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

    logger.info("%s abgeschlossen: %d Artikel", site_name, site_count)
    return site_count


def _taz_to_articles(taz_articles) -> list[Article]:
    return [
        Article(
            date=a.date, url=a.url, title=a.title, author=a.author,
            char_count=a.char_count, search_terms=[a.search_terms],
            paywall="", body_text=a.body_text,
        )
        for a in taz_articles
    ]


def _heise_to_articles(heise_articles) -> list[Article]:
    return [
        Article(
            date=a.date, url=a.url, title=a.title, author=a.author,
            char_count=a.char_count, search_terms=[a.search_terms],
            paywall="heise+" if a.is_heise_plus else "",
            body_text=a.body_text,
        )
        for a in heise_articles
    ]


def _zeit_to_articles(zeit_articles) -> list[Article]:
    return [
        Article(
            date=a.date, url=a.url, title=a.title, author=a.author,
            char_count=a.char_count, search_terms=[a.search_terms],
            paywall="Z+" if a.is_zplus else "",
            body_text=a.body_text,
        )
        for a in zeit_articles
    ]


async def run():
    config = load_config()
    pairs = config.all_keyword_pairs
    total = len(pairs) * 3

    logger.info(
        "%d Keyword-Paare × 3 Seiten = %d Suchen, Zeitraum %s – %s",
        len(pairs), total, config.date_start, config.date_end,
    )

    csv_path = Path("ergebnisse.csv")
    texte_dir = Path("texte")
    writer = IncrementalWriter(csv_path, texte_dir)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            taz_count = await _search_and_scrape(
                browser, "taz.de", taz_search, taz_scrape, _taz_to_articles,
                pairs, config, 0, writer,
            )
            heise_count = await _search_and_scrape(
                browser, "heise.de", heise_search, heise_scrape, _heise_to_articles,
                pairs, config, len(pairs), writer,
            )
            # Login once for all zeit.de keyword pairs
            zeit_creds = config.credentials.get("zeit")
            zeit_context = None
            if zeit_creds:
                zeit_context = await create_logged_in_context(
                    browser, zeit_creds.username, zeit_creds.password,
                )
            zeit_count = await _search_and_scrape(
                browser, "zeit.de", zeit_search, zeit_scrape, _zeit_to_articles,
                pairs, config, len(pairs) * 2, writer,
                scrape_kwargs={"logged_in_context": zeit_context},
            )
            if zeit_context:
                await zeit_context.close()
        finally:
            await browser.close()

    # --- Volltextfilter ---
    scrape_count = writer.article_count
    filter_result = filter_articles(csv_path, texte_dir)

    # Summary
    print(f"\n{'='*70}")
    print(f"Ergebnis: {filter_result.kept} Artikel (von {scrape_count} nach Volltextfilter)")
    print(f"  taz.de:   {taz_count} Artikel")
    print(f"  heise.de: {heise_count} Artikel")
    print(f"  zeit.de:  {zeit_count} Artikel")
    print(f"  Vor Filter: {scrape_count} | Nach Filter: {filter_result.kept} | Entfernt: {filter_result.removed}")
    print(f"  CSV: {csv_path}")
    print(f"  Texte: {texte_dir}/")
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
