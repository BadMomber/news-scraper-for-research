import csv
import logging
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

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
    body_text: str = ""


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
            body_text=a.body_text,
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
            body_text=a.body_text,
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
            body_text=a.body_text,
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


CSV_HEADER = [
    "Date", "Link", "Titel", "Autor",
    "Used Search Terms", "Character Count", "Paywall", "Textdatei",
]


def _url_to_slug(url: str, max_length: int = 120) -> str:
    """Convert a URL to a filesystem-safe slug for text file names."""
    parsed = urlparse(url)
    # Combine host and path, strip www. prefix
    raw = parsed.netloc.removeprefix("www.") + parsed.path
    # Replace non-alphanumeric with dashes, collapse multiple dashes
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw).strip("-").lower()
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    return slug


def _save_text_file(texte_dir: Path, url: str, text: str) -> str:
    """Save article text to a .txt file and return the filename."""
    slug = _url_to_slug(url)
    filename = f"{slug}.txt"
    filepath = texte_dir / filename
    filepath.write_text(text, encoding="utf-8")
    return filename


class IncrementalWriter:
    """Writes articles incrementally to CSV and text files.

    After each call to add_articles(), the CSV is up-to-date and
    text files exist for all articles. Deduplication runs against
    all previously added articles.
    """

    def __init__(self, csv_path: Path, texte_dir: Path):
        self.csv_path = csv_path
        self.texte_dir = texte_dir
        self._seen: dict[str, Article] = {}  # title -> Article
        self._text_files: dict[str, str] = {}  # title -> filename

        texte_dir.mkdir(parents=True, exist_ok=True)
        self._write_csv()

    def add_articles(self, articles: list[Article]) -> None:
        """Add a batch of articles, dedup, write text files, update CSV."""
        changed = False

        for article in articles:
            if article.title in self._seen:
                existing = self._seen[article.title]
                for term in article.search_terms:
                    if term not in existing.search_terms:
                        existing.search_terms.append(term)
                        changed = True
            else:
                self._seen[article.title] = article
                filename = _save_text_file(
                    self.texte_dir, article.url, article.body_text,
                )
                self._text_files[article.title] = filename
                changed = True

        if changed:
            self._write_csv()
            logger.info(
                "CSV aktualisiert: %s (%d Artikel)",
                self.csv_path, len(self._seen),
            )

    def _write_csv(self) -> None:
        """Write the full CSV from the current in-memory state."""
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
            for title, a in self._seen.items():
                writer.writerow([
                    a.date.isoformat(),
                    a.url,
                    a.title,
                    a.author,
                    "; ".join(a.search_terms),
                    a.char_count,
                    a.paywall,
                    self._text_files.get(title, ""),
                ])

    @property
    def article_count(self) -> int:
        return len(self._seen)
