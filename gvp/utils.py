from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Optional

__all__ = ["get_selected", "parse_human_date", "parse_preliminary_month"]


def get_selected(data: Iterable[Any], attr: str = "selected") -> Any:
    return next(option for option in data if option.has_attr(attr))


def parse_human_date(date: str) -> Optional[datetime]:
    if not date.strip():
        return None

    weekday, date = date.split()
    day, month = map(int, date.split(".")[:2])
    year = datetime.now().year
    if 1 <= month <= 7:
        year += 1

    return datetime(year, month, day)


def parse_preliminary_month(month: int) -> datetime:
    month += 7
    year = datetime.now().year
    if month > 12:
        month -= 12
        year += 1

    return datetime(year, month, 1)
