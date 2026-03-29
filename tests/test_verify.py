import csv
from pathlib import Path

import pytest

from src.verify import _read_csv, _titles_match


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "test.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Link", "Titel", "Autor", "Used Search Terms", "Character Count", "Paywall"])
        writer.writerow(["2025-10-01", "https://example.com", "Test Titel", "Autor", "a+b", "100", ""])
        writer.writerow(["2025-10-02", "https://example.com/2", "Zweiter Artikel", "B", "c+d", "200", "heise+"])
    return path


class TestReadCsv:
    def test_reads_all_rows(self, sample_csv):
        articles = _read_csv(sample_csv)
        assert len(articles) == 2

    def test_reads_fields(self, sample_csv):
        articles = _read_csv(sample_csv)
        assert articles[0]["Titel"] == "Test Titel"
        assert articles[0]["Link"] == "https://example.com"
        assert articles[0]["Date"] == "2025-10-01"

    def test_reads_utf8(self, tmp_path):
        path = tmp_path / "utf8.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Link", "Titel", "Autor", "Used Search Terms", "Character Count", "Paywall"])
            writer.writerow(["2025-10-01", "u", "Künstliche Intelligenz", "Müller", "KI+EU", "100", ""])
        articles = _read_csv(path)
        assert articles[0]["Titel"] == "Künstliche Intelligenz"


class TestTitlesMatch:
    def test_exact_match(self):
        assert _titles_match("Hello World", "Hello World") is True

    def test_whitespace_tolerance(self):
        assert _titles_match("Hello  World", "Hello World") is True

    def test_case_insensitive(self):
        assert _titles_match("Hello World", "hello world") is True

    def test_page_title_contains_csv(self):
        assert _titles_match("KI-Skandal", "Grok: KI-Skandal weitet sich aus") is True

    def test_csv_contains_page_title(self):
        assert _titles_match("KI-Skandal weitet sich aus", "KI-Skandal") is True

    def test_different_titles(self):
        assert _titles_match("Erster Artikel", "Zweiter Artikel") is False

    def test_empty_strings(self):
        assert _titles_match("", "") is True
