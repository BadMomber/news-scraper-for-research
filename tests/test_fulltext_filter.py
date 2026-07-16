import csv
from pathlib import Path

import pytest

from src.fulltext_filter import (
    FilterResult,
    _any_pair_matches,
    _count_term_occurrences,
    _keyword_pair_matches,
    filter_articles,
)


class TestKeywordPairMatches:
    def test_both_words_present(self):
        assert _keyword_pair_matches("Grok generiert Hitler-Bilder", "Grok+Hitler")

    def test_one_word_missing(self):
        assert not _keyword_pair_matches("Grok generiert Bilder", "Grok+Hitler")

    def test_case_insensitive(self):
        assert _keyword_pair_matches("grok und hitler", "Grok+Hitler")

    def test_words_not_adjacent(self):
        assert _keyword_pair_matches(
            "Grok ist ein KI-Modell. Es erzeugte Hitler-Bilder.",
            "Grok+Hitler",
        )

    def test_empty_text(self):
        assert not _keyword_pair_matches("", "Grok+Hitler")

    def test_umlaut_keywords(self):
        assert _keyword_pair_matches(
            "Künstliche Intelligenz und EU-Regulierung",
            "Künstliche Intelligenz+EU",
        )


class TestAnyPairMatches:
    def test_first_pair_matches(self):
        assert _any_pair_matches("Grok und Hitler", "Grok+Hitler; Grok+Deepfake")

    def test_second_pair_matches(self):
        assert _any_pair_matches("Grok und Deepfake", "Grok+Hitler; Grok+Deepfake")

    def test_no_pair_matches(self):
        assert not _any_pair_matches("Etwas anderes", "Grok+Hitler; Grok+Deepfake")

    def test_single_pair(self):
        assert _any_pair_matches("Grok und Hitler", "Grok+Hitler")


class TestCountTermOccurrences:
    def test_sums_occurrences_of_both_words(self):
        text = "Grok zeigt Hitler. Grok mag Hitler nicht. Grok bleibt."
        assert _count_term_occurrences(text, "Grok+Hitler") == 5

    def test_case_insensitive(self):
        assert _count_term_occurrences("grok GROK Grok", "Grok+Hitler") == 3

    def test_shared_word_across_pairs_counted_once(self):
        text = "Grok Grok Deepfake"
        assert _count_term_occurrences(text, "Grok+Hitler; Grok+Deepfake") == 3

    def test_empty_text(self):
        assert _count_term_occurrences("", "Grok+Hitler") == 0

    def test_counts_substring_occurrences(self):
        assert _count_term_occurrences("Groks Hitler-Bild", "Grok+Hitler") == 2


def _write_test_csv(csv_path: Path, rows: list[list[str]]) -> None:
    """Helper: write CSV with standard header + rows."""
    header = [
        "Date", "Link", "Titel", "Autor",
        "Used Search Terms", "Character Count", "Paywall", "Textdatei",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def _write_text_file(texte_dir: Path, filename: str, content: str) -> None:
    """Helper: write a text file."""
    (texte_dir / filename).write_text(content, encoding="utf-8")


# Passes all criteria for "Grok+Hitler": pair present, 4 term occurrences.
# The character count criterion uses the CSV column, not the text length.
MATCHING_TEXT = "Grok erzeugt Hitler-Bilder. Grok zeigt Hitler erneut."


class TestFilterArticles:
    def test_keeps_matching_article(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel A", "Autor", "Grok+Hitler", "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1
        assert result.removed == 0
        assert (texte_dir / "a.txt").exists()

    def test_removes_non_matching_article(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", "Ein ganz anderer Artikel")
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel A", "Autor", "Grok+Hitler", "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 0
        assert result.removed == 1
        assert not (texte_dir / "a.txt").exists()

    def test_mixed_matching_and_non_matching(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_text_file(texte_dir, "b.txt", "Etwas anderes")
        _write_test_csv(csv_path, [
            ["2025-10-01", "u1", "Match", "A", "Grok+Hitler", "2500", "", "a.txt"],
            ["2025-10-01", "u2", "NoMatch", "A", "Grok+Hitler", "2500", "", "b.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1
        assert result.removed == 1
        assert (texte_dir / "a.txt").exists()
        assert not (texte_dir / "b.txt").exists()

    def test_multiple_pairs_one_matches(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(
            texte_dir, "a.txt",
            "Ein Deepfake von Grok. Grok erstellt noch ein Deepfake.",
        )
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel", "A", "Grok+Hitler; Grok+Deepfake", "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1

    def test_csv_valid_after_filter(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_text_file(texte_dir, "b.txt", "Irrelevant")
        _write_test_csv(csv_path, [
            ["2025-10-01", "u1", "Keep", "A", "Grok+Hitler", "2500", "", "a.txt"],
            ["2025-10-01", "u2", "Remove", "A", "Grok+Hitler", "2500", "", "b.txt"],
        ])

        filter_articles(csv_path, texte_dir)

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)

        assert "Textdatei" in header
        assert len(rows) == 1
        assert rows[0][2] == "Keep"

    def test_empty_csv(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_test_csv(csv_path, [])

        result = filter_articles(csv_path, texte_dir)

        assert result.total == 0
        assert result.kept == 0
        assert result.removed == 0

    def test_removes_article_below_2000_chars(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Kurz", "A", "Grok+Hitler", "1999", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.removed == 1
        assert "1999" in result.removal_reasons["Kurz"]
        assert not (texte_dir / "a.txt").exists()

    def test_keeps_article_with_exactly_2000_chars(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Grenzfall", "A", "Grok+Hitler", "2000", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1

    def test_removes_article_with_three_term_occurrences(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        # Pair matches, but only 3 occurrences total (Grok 2x, Hitler 1x)
        _write_text_file(texte_dir, "a.txt", "Grok und Hitler und Grok")
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Wenig", "A", "Grok+Hitler", "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.removed == 1
        assert "Suchbegriff-Treffer" in result.removal_reasons["Wenig"]
        assert not (texte_dir / "a.txt").exists()

    def test_keeps_article_with_exactly_four_term_occurrences(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        # Exactly 4 occurrences (Grok 2x, Hitler 2x)
        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Grenzfall", "A", "Grok+Hitler", "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1

    def test_char_count_fallback_to_text_length(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        # Empty Character Count column: fall back to actual text length
        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "OhneCount", "A", "Grok+Hitler", "", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.removed == 1
        assert "Zeichen" in result.removal_reasons["OhneCount"]

    def test_removed_titles_in_result(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", "Nichts relevantes")
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Mein Titel", "A", "Grok+Hitler", "100", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert "Mein Titel" in result.removed_titles

    def test_custom_thresholds(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        # 2 term occurrences, 100 chars: fails defaults, passes custom thresholds
        _write_text_file(texte_dir, "a.txt", "Grok trifft Hitler")
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel", "A", "Grok+Hitler", "100", "", "a.txt"],
        ])

        result = filter_articles(
            csv_path, texte_dir, min_char_count=50, min_term_occurrences=2,
        )

        assert result.kept == 1

    def test_case_insensitive_filter(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", "grok und hitler, GROK mag HITLER")
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel", "A", "Grok+Hitler", "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1
