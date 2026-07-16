import csv
from pathlib import Path

import pytest

from src.fulltext_filter import (
    FilterResult,
    _any_pair_matches,
    _count_matching_pairs,
    _keyword_pair_matches,
    _split_pairs,
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


class TestSplitPairs:
    def test_splits_and_strips(self):
        assert _split_pairs("Grok+Hitler; Grok+Deepfake") == {
            "Grok+Hitler", "Grok+Deepfake",
        }

    def test_duplicates_collapse(self):
        assert _split_pairs("Grok+Hitler; Grok+Hitler") == {"Grok+Hitler"}

    def test_empty_string(self):
        assert _split_pairs("") == set()


class TestCountMatchingPairs:
    def test_all_pairs_match(self):
        text = "Grok erzeugt Hitler-Deepfakes, sagt xAI, ohne Verantwortung."
        pairs = {"Grok+Hitler", "Grok+Deepfake", "Grok+xAI", "Grok+Verantwortung"}
        assert _count_matching_pairs(text, pairs) == 4

    def test_partially_matched_pair_not_counted(self):
        # Hitler present, Deepfake missing: only the first pair counts
        text = "Grok erzeugt Hitler-Bilder"
        assert _count_matching_pairs(text, {"Grok+Hitler", "Grok+Deepfake"}) == 1

    def test_repeated_words_count_pair_once(self):
        # Word frequency is irrelevant: one fully present pair counts once
        text = "Grok Grok Grok Grok und Hitler Hitler"
        assert _count_matching_pairs(text, {"Grok+Hitler"}) == 1

    def test_case_insensitive(self):
        assert _count_matching_pairs("grok und HITLER", {"Grok+Hitler"}) == 1

    def test_empty_text(self):
        assert _count_matching_pairs("", {"Grok+Hitler"}) == 0


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


# Passes all criteria: 4 distinct pairs fully present in the text.
# The character count criterion uses the CSV column, not the text length.
MATCHING_TERMS = "Grok+Hitler; Grok+Deepfake; Grok+xAI; Grok+Verantwortung"
MATCHING_TEXT = "Grok erzeugt Hitler-Deepfakes, sagt xAI, ohne Verantwortung."


class TestFilterArticles:
    def test_keeps_matching_article(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel A", "Autor", MATCHING_TERMS, "2500", "", "a.txt"],
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
            ["2025-10-01", "u1", "Match", "A", MATCHING_TERMS, "2500", "", "a.txt"],
            ["2025-10-01", "u2", "NoMatch", "A", MATCHING_TERMS, "2500", "", "b.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1
        assert result.removed == 1
        assert (texte_dir / "a.txt").exists()
        assert not (texte_dir / "b.txt").exists()

    def test_removes_article_with_three_matching_pairs(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        # Only 3 of 4 pairs fully present (Verantwortung missing)
        _write_text_file(
            texte_dir, "a.txt",
            "Grok erzeugt Hitler-Deepfakes, sagt xAI.",
        )
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Wenig", "A", MATCHING_TERMS, "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.removed == 1
        assert "Suchbegriff-Kombinationen (3)" in result.removal_reasons["Wenig"]
        assert not (texte_dir / "a.txt").exists()

    def test_word_frequency_does_not_help(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        # Many occurrences of one pair are still just one combination
        _write_text_file(
            texte_dir, "a.txt",
            "Grok Grok Grok Grok und Hitler Hitler Hitler Hitler",
        )
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "EinPaar", "A", "Grok+Hitler", "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.removed == 1
        assert "Suchbegriff-Kombinationen (1)" in result.removal_reasons["EinPaar"]

    def test_pairs_from_other_articles_count(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        # Article B was found via a single pair, but its text contains
        # four pairs known from the crawl (assigned to article A) —
        # the pair universe spans the whole CSV, so B is kept
        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_text_file(texte_dir, "b.txt", MATCHING_TEXT)
        _write_test_csv(csv_path, [
            ["2025-10-01", "u1", "Viele Paare", "A", MATCHING_TERMS, "2500", "", "a.txt"],
            ["2025-10-01", "u2", "Ein Paar", "A", "Grok+Hitler", "2500", "", "b.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 2
        assert result.removed == 0

    def test_removes_article_below_2000_chars(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Kurz", "A", MATCHING_TERMS, "1999", "", "a.txt"],
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
            ["2025-10-01", "url", "Grenzfall", "A", MATCHING_TERMS, "2000", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1

    def test_keeps_article_with_exactly_four_matching_pairs(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        # 4 of 5 pairs fully present (Musk missing)
        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Grenzfall", "A",
             MATCHING_TERMS + "; Grok+Musk", "2500", "", "a.txt"],
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
            ["2025-10-01", "url", "OhneCount", "A", MATCHING_TERMS, "", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.removed == 1
        assert "Zeichen" in result.removal_reasons["OhneCount"]

    def test_csv_valid_after_filter(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT)
        _write_text_file(texte_dir, "b.txt", "Irrelevant")
        _write_test_csv(csv_path, [
            ["2025-10-01", "u1", "Keep", "A", MATCHING_TERMS, "2500", "", "a.txt"],
            ["2025-10-01", "u2", "Remove", "A", MATCHING_TERMS, "2500", "", "b.txt"],
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

    def test_removed_titles_in_result(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", "Nichts relevantes")
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Mein Titel", "A", "Grok+Hitler", "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert "Mein Titel" in result.removed_titles

    def test_case_insensitive_filter(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", MATCHING_TEXT.lower())
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel", "A", MATCHING_TERMS, "2500", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1
