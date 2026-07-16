import argparse
import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Hard exclusion criteria (thesis methodology): articles with fewer than
# 2000 characters or fewer than four distinct fully matched keyword pairs
# in the body are removed. Boundary values (exactly 2000 / exactly 4) are
# kept. A pair counts as matched when both of its words appear somewhere
# in the text, regardless of how often. Matching runs against ALL pairs
# used in the crawl (union of "Used Search Terms" across the whole CSV),
# not only the pairs the article itself was found with.
MIN_CHAR_COUNT = 2000
MIN_MATCHING_PAIRS = 4


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


def _split_pairs(search_terms: str) -> set[str]:
    """Split a "Grok+Hitler; Grok+Deepfake" string into a set of pairs."""
    return {p.strip() for p in search_terms.split(";") if p.strip()}


def _count_matching_pairs(text: str, pairs: set[str]) -> int:
    """Count distinct keyword pairs that are fully present in text.

    A pair counts when both of its words appear anywhere in the text
    (case-insensitive), regardless of how often.
    """
    return sum(1 for pair in pairs if _keyword_pair_matches(text, pair))


def _exclusion_reason(
    text: str, search_terms: str, char_count: int, all_pairs: set[str],
) -> str | None:
    """Return why an article is excluded, or None if it passes all criteria.

    all_pairs is the union of every keyword pair used in the crawl; the
    combination count runs against this set, while the basic relevance
    check (AP10) still uses only the article's own search_terms.
    """
    if not _any_pair_matches(text, search_terms):
        return "kein Suchbegriff-Paar im Text"
    if char_count < MIN_CHAR_COUNT:
        return f"unter {MIN_CHAR_COUNT} Zeichen ({char_count})"
    matching_pairs = _count_matching_pairs(text, all_pairs)
    if matching_pairs < MIN_MATCHING_PAIRS:
        return (
            f"weniger als {MIN_MATCHING_PAIRS} Suchbegriff-Kombinationen"
            f" ({matching_pairs})"
        )
    return None


def filter_articles(csv_path: Path, texte_dir: Path) -> FilterResult:
    """Apply the hard exclusion criteria to already crawled results.

    Removes articles whose text contains none of their keyword pairs,
    has fewer than MIN_CHAR_COUNT characters, or fewer than
    MIN_MATCHING_PAIRS fully matched keyword pairs (checked against all
    pairs used in the crawl). Rewrites the CSV with only the kept
    articles and deletes text files of removed ones.
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

    # Pair universe: every keyword pair the crawl used, across all articles
    all_pairs: set[str] = set()
    for row in rows:
        all_pairs |= _split_pairs(row[search_terms_idx])
    logger.info("Volltextfilter: %d Keyword-Paare im Crawl verwendet", len(all_pairs))

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

        reason = _exclusion_reason(text, search_terms, char_count, all_pairs)
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
