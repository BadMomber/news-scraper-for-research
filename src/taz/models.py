from dataclasses import dataclass
from datetime import date


@dataclass
class TazSearchResult:
    title: str
    url: str
    date: date
