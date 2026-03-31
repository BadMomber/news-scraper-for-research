from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml


@dataclass
class SiteCredentials:
    username: str
    password: str


@dataclass
class SearchConfig:
    search_terms: dict[str, list[list[str]]]
    target_sites: list[str]
    date_start: date
    date_end: date
    credentials: dict[str, SiteCredentials] = field(default_factory=dict)

    @property
    def all_keyword_pairs(self) -> list[list[str]]:
        """Returns a flat list of all keyword pairs across all categories."""
        pairs = []
        for category_pairs in self.search_terms.values():
            pairs.extend(category_pairs)
        return pairs


def load_config(path: Path | None = None) -> SearchConfig:
    """Load search configuration from seed.yaml."""
    if path is None:
        path = Path(__file__).parent.parent / "seed.yaml"

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    credentials: dict[str, SiteCredentials] = {}
    for site, creds in raw.get("credentials", {}).items():
        credentials[site] = SiteCredentials(
            username=creds["username"],
            password=creds["password"],
        )

    return SearchConfig(
        search_terms=raw["search_terms"],
        target_sites=raw["target_sites"],
        date_start=date.fromisoformat(raw["date_range"]["start"]),
        date_end=date.fromisoformat(raw["date_range"]["end"]),
        credentials=credentials,
    )
