from dataclasses import dataclass
from datetime import date


@dataclass
class ZeitSearchResult:
    title: str
    url: str
    date: date
    is_zplus: bool
