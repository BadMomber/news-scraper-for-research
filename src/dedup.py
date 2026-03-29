import csv
import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from src.heise.models import HeiseArticle
from src.taz.models import TazArticle
from src.zeit.models import ZeitArticle

logger = logging.getLogger(__name__)


@dataclass
class Article:
    date: date
    url: str
    title: str
    author: str
    char_count: int
    search_terms: list[str] = field(default_factory=list)
    paywall: str = ""


def to_articles(
    taz: list[TazArticle],
    heise: list[HeiseArticle],
    zeit: list[ZeitArticle],
) -> list[Article]:
    """Convert site-specific article types to unified Article format."""
    articles: list[Article] = []

    for a in taz:
        articles.append(Article(
            date=a.date,
            url=a.url,
            title=a.title,
            author=a.author,
            char_count=a.char_count,
            search_terms=[a.search_terms],
            paywall="",
        ))

    for a in heise:
        articles.append(Article(
            date=a.date,
            url=a.url,
            title=a.title,
            author=a.author,
            char_count=a.char_count,
            search_terms=[a.search_terms],
            paywall="heise+" if a.is_heise_plus else "",
        ))

    for a in zeit:
        articles.append(Article(
            date=a.date,
            url=a.url,
            title=a.title,
            author=a.author,
            char_count=a.char_count,
            search_terms=[a.search_terms],
            paywall="Z+" if a.is_zplus else "",
        ))

    return articles


def deduplicate(articles: list[Article]) -> list[Article]:
    """Deduplicate articles by exact title match.

    When duplicates are found, the first occurrence is kept and
    search_terms from all duplicates are merged (preserving order).
    """
    seen: dict[str, Article] = {}

    for article in articles:
        if article.title in seen:
            existing = seen[article.title]
            for term in article.search_terms:
                if term not in existing.search_terms:
                    existing.search_terms.append(term)
        else:
            seen[article.title] = article

    result = list(seen.values())
    logger.info(
        "Deduplizierung: %d Artikel → %d eindeutige",
        len(articles), len(result),
    )
    return result


def export_csv(articles: list[Article], path: Path | None = None) -> Path:
    """Export articles to UTF-8 CSV file.

    Columns: Date, Link, Titel, Autor, Used Search Terms, Character Count, Paywall
    """
    if path is None:
        path = Path("ergebnisse.csv")

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Date", "Link", "Titel", "Autor",
            "Used Search Terms", "Character Count", "Paywall",
        ])

        for a in articles:
            writer.writerow([
                a.date.isoformat(),
                a.url,
                a.title,
                a.author,
                "; ".join(a.search_terms),
                a.char_count,
                a.paywall,
            ])

    logger.info("CSV exportiert: %s (%d Artikel)", path, len(articles))
    return path
