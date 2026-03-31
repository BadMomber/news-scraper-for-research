import csv
from pathlib import Path

import pytest

from src.fulltext_filter import (
    FilterResult,
    _any_pair_matches,
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


class TestFilterArticles:
    def test_keeps_matching_article(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", "Grok erzeugt Hitler-Bilder")
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel A", "Autor", "Grok+Hitler", "100", "", "a.txt"],
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
            ["2025-10-01", "url", "Titel A", "Autor", "Grok+Hitler", "100", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 0
        assert result.removed == 1
        assert not (texte_dir / "a.txt").exists()

    def test_mixed_matching_and_non_matching(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", "Grok und Hitler")
        _write_text_file(texte_dir, "b.txt", "Etwas anderes")
        _write_test_csv(csv_path, [
            ["2025-10-01", "u1", "Match", "A", "Grok+Hitler", "100", "", "a.txt"],
            ["2025-10-01", "u2", "NoMatch", "A", "Grok+Hitler", "100", "", "b.txt"],
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

        _write_text_file(texte_dir, "a.txt", "Ein Deepfake von Grok erstellt")
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel", "A", "Grok+Hitler; Grok+Deepfake", "100", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1

    def test_csv_valid_after_filter(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", "Grok und Hitler")
        _write_text_file(texte_dir, "b.txt", "Irrelevant")
        _write_test_csv(csv_path, [
            ["2025-10-01", "u1", "Keep", "A", "Grok+Hitler", "100", "", "a.txt"],
            ["2025-10-01", "u2", "Remove", "A", "Grok+Hitler", "100", "", "b.txt"],
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
            ["2025-10-01", "url", "Mein Titel", "A", "Grok+Hitler", "100", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert "Mein Titel" in result.removed_titles

    def test_case_insensitive_filter(self, tmp_path):
        csv_path = tmp_path / "out.csv"
        texte_dir = tmp_path / "texte"
        texte_dir.mkdir()

        _write_text_file(texte_dir, "a.txt", "grok und hitler im text")
        _write_test_csv(csv_path, [
            ["2025-10-01", "url", "Titel", "A", "Grok+Hitler", "100", "", "a.txt"],
        ])

        result = filter_articles(csv_path, texte_dir)

        assert result.kept == 1
