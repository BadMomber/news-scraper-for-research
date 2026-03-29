import csv
from datetime import date
from pathlib import Path

import pytest

from src.dedup import Article, deduplicate, export_csv, to_articles
from src.heise.models import HeiseArticle
from src.taz.models import TazArticle
from src.zeit.models import ZeitArticle


class TestToArticles:
    def test_converts_taz(self):
        taz = [TazArticle(date(2025, 10, 1), "u", "T", "A", 100, "Grok+Hitler")]
        result = to_articles(taz, [], [])

        assert len(result) == 1
        assert result[0].title == "T"
        assert result[0].paywall == ""
        assert result[0].search_terms == ["Grok+Hitler"]

    def test_converts_heise_plus(self):
        heise = [HeiseArticle(date(2025, 10, 1), "u", "T", "A", 100, "Grok+Hitler", True)]
        result = to_articles([], heise, [])

        assert result[0].paywall == "heise+"

    def test_converts_heise_free(self):
        heise = [HeiseArticle(date(2025, 10, 1), "u", "T", "A", 100, "Grok+Hitler", False)]
        result = to_articles([], heise, [])

        assert result[0].paywall == ""

    def test_converts_zeit_zplus(self):
        zeit = [ZeitArticle(date(2025, 10, 1), "u", "T", "A", 100, "Grok+Hitler", True)]
        result = to_articles([], [], zeit)

        assert result[0].paywall == "Z+"

    def test_combines_all_sites(self):
        taz = [TazArticle(date(2025, 10, 1), "u1", "T1", "A", 100, "a+b")]
        heise = [HeiseArticle(date(2025, 10, 2), "u2", "T2", "A", 200, "a+b", False)]
        zeit = [ZeitArticle(date(2025, 10, 3), "u3", "T3", "A", 300, "a+b", False)]
        result = to_articles(taz, heise, zeit)

        assert len(result) == 3


class TestDeduplicate:
    def test_no_duplicates(self):
        articles = [
            Article(date(2025, 10, 1), "u1", "Title A", "A", 100, ["Grok+Hitler"]),
            Article(date(2025, 10, 2), "u2", "Title B", "B", 200, ["Grok+Hitler"]),
        ]
        result = deduplicate(articles)

        assert len(result) == 2

    def test_merges_duplicates(self):
        articles = [
            Article(date(2025, 10, 1), "u1", "Same Title", "A", 100, ["Grok+Hitler"]),
            Article(date(2025, 10, 1), "u1", "Same Title", "A", 100, ["Grok+Deepfake"]),
        ]
        result = deduplicate(articles)

        assert len(result) == 1
        assert result[0].search_terms == ["Grok+Hitler", "Grok+Deepfake"]

    def test_keeps_first_occurrence(self):
        articles = [
            Article(date(2025, 10, 1), "url1", "Title", "Author1", 100, ["a+b"]),
            Article(date(2025, 10, 2), "url2", "Title", "Author2", 200, ["c+d"]),
        ]
        result = deduplicate(articles)

        assert result[0].url == "url1"
        assert result[0].author == "Author1"

    def test_no_duplicate_search_terms(self):
        articles = [
            Article(date(2025, 10, 1), "u", "Title", "A", 100, ["Grok+Hitler"]),
            Article(date(2025, 10, 1), "u", "Title", "A", 100, ["Grok+Hitler"]),
        ]
        result = deduplicate(articles)

        assert result[0].search_terms == ["Grok+Hitler"]

    def test_empty_list(self):
        assert deduplicate([]) == []

    def test_preserves_order(self):
        articles = [
            Article(date(2025, 10, 1), "u", "Title", "A", 100, ["a+b"]),
            Article(date(2025, 10, 1), "u", "Title", "A", 100, ["c+d"]),
            Article(date(2025, 10, 1), "u", "Title", "A", 100, ["e+f"]),
        ]
        result = deduplicate(articles)

        assert result[0].search_terms == ["a+b", "c+d", "e+f"]


class TestExportCsv:
    def test_creates_csv_file(self, tmp_path):
        articles = [
            Article(date(2025, 10, 1), "https://example.com", "Test Titel", "Max Müller", 1234, ["Grok+Hitler"], ""),
        ]
        path = export_csv(articles, tmp_path / "test.csv")

        assert path.exists()

    def test_csv_has_header(self, tmp_path):
        path = export_csv([], tmp_path / "test.csv")

        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)

        assert header == ["Date", "Link", "Titel", "Autor", "Used Search Terms", "Character Count", "Paywall"]

    def test_csv_content(self, tmp_path):
        articles = [
            Article(date(2025, 10, 1), "https://example.com", "Test", "Autor", 100, ["Grok+Hitler", "Grok+Deepfake"], "heise+"),
        ]
        path = export_csv(articles, tmp_path / "test.csv")

        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            row = next(reader)

        assert row[0] == "2025-10-01"
        assert row[1] == "https://example.com"
        assert row[2] == "Test"
        assert row[3] == "Autor"
        assert row[4] == "Grok+Hitler; Grok+Deepfake"
        assert row[5] == "100"
        assert row[6] == "heise+"

    def test_csv_utf8_umlauts(self, tmp_path):
        articles = [
            Article(date(2025, 10, 1), "u", "Künstliche Intelligenz", "Hans Müller", 100, ["KI+EU"], ""),
        ]
        path = export_csv(articles, tmp_path / "test.csv")

        with open(path, encoding="utf-8") as f:
            content = f.read()

        assert "Künstliche Intelligenz" in content
        assert "Müller" in content

    def test_csv_escapes_commas(self, tmp_path):
        articles = [
            Article(date(2025, 10, 1), "u", "Titel, mit Komma", "A", 100, ["a+b"], ""),
        ]
        path = export_csv(articles, tmp_path / "test.csv")

        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            row = next(reader)

        assert row[2] == "Titel, mit Komma"

    def test_default_path(self):
        articles = []
        path = export_csv(articles)

        assert path == Path("ergebnisse.csv")
        path.unlink()  # cleanup
