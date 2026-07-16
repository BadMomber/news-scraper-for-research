import argparse
import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Hard exclusion criteria (thesis methodology): articles with fewer than
# 2000 characters or fewer than four search-term occurrences in the body
# are removed. Boundary values (exactly 2000 / exactly 4) are kept.
MIN_CHAR_COUNT = 2000
MIN_TERM_OCCURRENCES = 4


@dataclass
class FilterResult:
    total: int
    kept: int
    removed: int
    removed_titles: list[str] = field(default_factory=list)
    removal_reasons: dict[str, str] = field(default_factory=dict)


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


def _unique_keywords(search_terms: str) -> set[str]:
    """Extract unique lowercase keywords from all pairs.

    search_terms format: "Grok+Hitler; Grok+Deepfake"
    A keyword shared by several pairs (here "Grok") is counted once.
    """
    return {
        word.strip().lower()
        for pair in search_terms.split(";")
        for word in pair.split("+")
        if word.strip()
    }


def _count_term_occurrences(text: str, search_terms: str) -> int:
    """Sum all occurrences of all unique keywords in text (case-insensitive)."""
    text_lower = text.lower()
    return sum(text_lower.count(word) for word in _unique_keywords(search_terms))


def _exclusion_reason(text: str, search_terms: str, char_count: int) -> str | None:
    """Return why an article is excluded, or None if it passes all criteria."""
    if not _any_pair_matches(text, search_terms):
        return "kein Suchbegriff-Paar im Text"
    if char_count < MIN_CHAR_COUNT:
        return f"unter {MIN_CHAR_COUNT} Zeichen ({char_count})"
    occurrences = _count_term_occurrences(text, search_terms)
    if occurrences < MIN_TERM_OCCURRENCES:
        return (
            f"weniger als {MIN_TERM_OCCURRENCES} Suchbegriff-Treffer"
            f" ({occurrences})"
        )
    return None


def filter_articles(csv_path: Path, texte_dir: Path) -> FilterResult:
    """Apply the hard exclusion criteria to already crawled results.

    Removes articles whose text contains none of their keyword pairs,
    has fewer than MIN_CHAR_COUNT characters, or fewer than
    MIN_TERM_OCCURRENCES search-term occurrences. Rewrites the CSV with
    only the kept articles and deletes text files of removed ones.
    """
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    kept_rows: list[list[str]] = []
    removed_titles: list[str] = []
    removal_reasons: dict[str, str] = {}

    search_terms_idx = header.index("Used Search Terms")
    char_count_idx = header.index("Character Count")
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

        try:
            char_count = int(row[char_count_idx])
        except ValueError:
            char_count = len(text)

        reason = _exclusion_reason(text, search_terms, char_count)
        if reason is None:
            kept_rows.append(row)
        else:
            removed_titles.append(title)
            removal_reasons[title] = reason
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
        removal_reasons=removal_reasons,
    )

    logger.info(
        "Volltextfilter: %d Artikel → %d behalten, %d entfernt",
        result.total, result.kept, result.removed,
    )
    for title in removed_titles:
        logger.info("  Entfernt (%s): %s", removal_reasons[title], title)

    return result


def main() -> None:
    """Apply the filter to existing crawl results without re-crawling."""
    parser = argparse.ArgumentParser(
        description=(
            "Wendet die harten Ausschlusskriterien auf bereits gecrawlte "
            "Ergebnisse an (CSV wird neu geschrieben, Textdateien "
            "aussortierter Artikel werden gelöscht)."
        ),
    )
    parser.add_argument(
        "--csv", type=Path, default=Path("ergebnisse.csv"),
        help="Pfad zur Ergebnis-CSV (Default: ergebnisse.csv)",
    )
    parser.add_argument(
        "--texte", type=Path, default=Path("texte"),
        help="Verzeichnis mit den Artikel-Textdateien (Default: texte/)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    filter_articles(args.csv, args.texte)


if __name__ == "__main__":
    main()
