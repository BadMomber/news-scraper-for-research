from dataclasses import dataclass
from datetime import date


@dataclass
class HeiseSearchResult:
    title: str
    url: str
    date: date
    is_heise_plus: bool
