import csv
from datetime import date
from pathlib import Path

import pytest

from src.dedup import (
    Article, IncrementalWriter, _url_to_slug, _save_text_file,
    deduplicate, export_csv, to_articles,
)
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


class TestUrlToSlug:
    def test_taz_url(self):
        slug = _url_to_slug("https://taz.de/Grok-und-Hitler/!6053194/")
        assert slug == "taz-de-grok-und-hitler-6053194"

    def test_heise_url(self):
        slug = _url_to_slug("https://www.heise.de/news/Deepfake-Betrug-1234567.html")
        assert slug == "heise-de-news-deepfake-betrug-1234567-html"

    def test_zeit_url(self):
        slug = _url_to_slug("https://www.zeit.de/digital/2025-01/ki-artikel")
        assert slug == "zeit-de-digital-2025-01-ki-artikel"

    def test_strips_www(self):
        slug = _url_to_slug("https://www.example.com/path")
        assert slug.startswith("example-com")

    def test_truncates_long_slugs(self):
        long_url = "https://example.com/" + "a" * 200
        slug = _url_to_slug(long_url, max_length=50)
        assert len(slug) <= 50


class TestSaveTextFile:
    def test_creates_file(self, tmp_path):
        filename = _save_text_file(tmp_path, "https://taz.de/Artikel/!123/", "Hallo Welt")
        assert (tmp_path / filename).exists()
        assert (tmp_path / filename).read_text(encoding="utf-8") == "Hallo Welt"

    def test_filename_is_slug(self, tmp_path):
        filename = _save_text_file(tmp_path, "https://taz.de/Test/!999/", "text")
        assert filename == "taz-de-test-999.txt"


class TestIncrementalWriter:
    def _make_article(self, title="Test", url="https://example.com/test",
                      search_terms=None, body_text="Artikeltext"):
        return Article(
            date=date(2025, 10, 1), url=url, title=title, author="Autor",
            char_count=len(body_text), search_terms=search_terms or ["a+b"],
            paywall="", body_text=body_text,
        )

    def test_creates_csv_with_header(self, tmp_path):
        writer = IncrementalWriter(tmp_path / "out.csv", tmp_path / "texte")

        with open(tmp_path / "out.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)

        assert "Textdatei" in header

    def test_creates_texte_dir(self, tmp_path):
        IncrementalWriter(tmp_path / "out.csv", tmp_path / "texte")
        assert (tmp_path / "texte").is_dir()

    def test_add_articles_writes_csv_and_text(self, tmp_path):
        writer = IncrementalWriter(tmp_path / "out.csv", tmp_path / "texte")
        writer.add_articles([self._make_article()])

        # CSV has one data row
        with open(tmp_path / "out.csv", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert len(rows) == 2  # header + 1 article

        # Text file exists
        text_filename = rows[1][7]  # Textdatei column
        assert (tmp_path / "texte" / text_filename).exists()
        assert (tmp_path / "texte" / text_filename).read_text(encoding="utf-8") == "Artikeltext"

    def test_dedup_merges_search_terms(self, tmp_path):
        writer = IncrementalWriter(tmp_path / "out.csv", tmp_path / "texte")

        writer.add_articles([self._make_article(search_terms=["a+b"])])
        writer.add_articles([self._make_article(search_terms=["c+d"])])

        assert writer.article_count == 1

        with open(tmp_path / "out.csv", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert rows[1][4] == "a+b; c+d"  # Used Search Terms

    def test_incremental_two_batches(self, tmp_path):
        writer = IncrementalWriter(tmp_path / "out.csv", tmp_path / "texte")

        writer.add_articles([self._make_article(title="A", url="https://example.com/a")])
        writer.add_articles([self._make_article(title="B", url="https://example.com/b")])

        assert writer.article_count == 2

        with open(tmp_path / "out.csv", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert len(rows) == 3  # header + 2

    def test_text_file_not_duplicated(self, tmp_path):
        writer = IncrementalWriter(tmp_path / "out.csv", tmp_path / "texte")

        writer.add_articles([self._make_article(search_terms=["a+b"])])
        writer.add_articles([self._make_article(search_terms=["c+d"])])

        text_files = list((tmp_path / "texte").iterdir())
        assert len(text_files) == 1
