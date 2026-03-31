import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FilterResult:
    total: int
    kept: int
    removed: int
    removed_titles: list[str] = field(default_factory=list)


def _keyword_pair_matches(text: str, keyword_pair: str) -> bool:
    """Check if both words of a keyword pair appear in text (case-insensitive).

    keyword_pair format: "Grok+Hitler"
    """
    words = keyword_pair.split("+")
    text_lower = text.lower()
    return all(word.lower() in text_lower for word in words)


def _any_pair_matches(text: str, search_terms: str) -> bool:
    """Check if at least one keyword pair from search_terms matches.

    search_terms format: "Grok+Hitler; Grok+Deepfake"
    """
    pairs = [p.strip() for p in search_terms.split(";")]
    return any(_keyword_pair_matches(text, pair) for pair in pairs)


def filter_articles(csv_path: Path, texte_dir: Path) -> FilterResult:
    """Remove articles whose text doesn't contain any of their keyword pairs.

    Reads the CSV, checks each article's text file, rewrites CSV with only
    matching articles, and deletes text files for removed articles.
    """
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    kept_rows: list[list[str]] = []
    removed_titles: list[str] = []

    search_terms_idx = header.index("Used Search Terms")
    textdatei_idx = header.index("Textdatei")
    titel_idx = header.index("Titel")

    for row in rows:
        search_terms = row[search_terms_idx]
        text_filename = row[textdatei_idx]
        title = row[titel_idx]

        text_path = texte_dir / text_filename
        if text_path.exists():
            text = text_path.read_text(encoding="utf-8")
        else:
            text = ""

        if _any_pair_matches(text, search_terms):
            kept_rows.append(row)
        else:
            removed_titles.append(title)
            if text_path.exists():
                text_path.unlink()

    # Rewrite CSV with only kept articles
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(kept_rows)

    result = FilterResult(
        total=len(rows),
        kept=len(kept_rows),
        removed=len(removed_titles),
        removed_titles=removed_titles,
    )

    logger.info(
        "Volltextfilter: %d Artikel → %d behalten, %d entfernt",
        result.total, result.kept, result.removed,
    )
    for title in removed_titles:
        logger.info("  Entfernt: %s", title)

    return result
