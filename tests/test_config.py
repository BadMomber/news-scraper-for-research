from datetime import date
from pathlib import Path

import yaml

from src.config import SiteCredentials, load_config


SEED_PATH = Path(__file__).parent.parent / "seed.yaml"


def test_load_config_returns_search_config():
    config = load_config(SEED_PATH)
    assert config is not None


def test_load_config_has_17_keyword_pairs():
    config = load_config(SEED_PATH)
    assert len(config.all_keyword_pairs) == 17


def test_load_config_has_3_categories():
    config = load_config(SEED_PATH)
    assert len(config.search_terms) == 3
    assert "grok_skandale" in config.search_terms
    assert "intersektion_ki_grok" in config.search_terms
    assert "meta_diskurs" in config.search_terms


def test_load_config_has_3_target_sites():
    config = load_config(SEED_PATH)
    assert len(config.target_sites) == 3
    assert "https://taz.de" in config.target_sites
    assert "https://www.zeit.de" in config.target_sites
    assert "https://www.heise.de" in config.target_sites


def test_load_config_has_correct_date_range():
    config = load_config(SEED_PATH)
    assert config.date_start == date(2025, 7, 8)
    assert config.date_end == date(2026, 2, 8)


def test_keyword_pairs_are_lists_of_two_strings():
    config = load_config(SEED_PATH)
    for pair in config.all_keyword_pairs:
        assert len(pair) == 2
        assert isinstance(pair[0], str)
        assert isinstance(pair[1], str)


def test_keyword_pairs_contain_umlauts():
    config = load_config(SEED_PATH)
    pairs_flat = [term for pair in config.all_keyword_pairs for term in pair]
    assert "Künstliche Intelligenz" in pairs_flat


def test_load_config_reads_credentials():
    config = load_config(SEED_PATH)
    assert "zeit" in config.credentials
    assert isinstance(config.credentials["zeit"], SiteCredentials)
    assert config.credentials["zeit"].username != ""
    assert config.credentials["zeit"].password != ""


def test_load_config_without_credentials(tmp_path):
    seed = {
        "search_terms": {"cat": [["a", "b"]]},
        "target_sites": ["https://example.com"],
        "date_range": {"start": "2025-01-01", "end": "2025-12-31"},
    }
    path = tmp_path / "seed.yaml"
    path.write_text(yaml.dump(seed), encoding="utf-8")

    config = load_config(path)

    assert config.credentials == {}


def test_load_config_partial_credentials(tmp_path):
    seed = {
        "search_terms": {"cat": [["a", "b"]]},
        "target_sites": ["https://example.com"],
        "date_range": {"start": "2025-01-01", "end": "2025-12-31"},
        "credentials": {
            "zeit": {"username": "user", "password": "pass"},
        },
    }
    path = tmp_path / "seed.yaml"
    path.write_text(yaml.dump(seed), encoding="utf-8")

    config = load_config(path)

    assert "zeit" in config.credentials
    assert "heise" not in config.credentials
