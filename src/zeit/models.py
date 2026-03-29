from dataclasses import dataclass
from datetime import date


@dataclass
class ZeitSearchResult:
    title: str
    url: str
    date: date
    is_zplus: bool


@dataclass
class ZeitArticle:
    date: date
    url: str
    title: str
    author: str
    char_count: int
    search_terms: str
    is_zplus: bool
