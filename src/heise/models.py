from dataclasses import dataclass
from datetime import date


@dataclass
class HeiseSearchResult:
    title: str
    url: str
    date: date
    is_heise_plus: bool


@dataclass
class HeiseArticle:
    date: date
    url: str
    title: str
    author: str
    char_count: int
    search_terms: str
    is_heise_plus: bool
    body_text: str = ""
