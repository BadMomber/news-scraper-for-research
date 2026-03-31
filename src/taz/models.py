from dataclasses import dataclass
from datetime import date


@dataclass
class TazSearchResult:
    title: str
    url: str
    date: date


@dataclass
class TazArticle:
    date: date
    url: str
    title: str
    author: str
    char_count: int
    search_terms: str
    body_text: str = ""
