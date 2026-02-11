from datetime import date, datetime
from typing import Any, Dict, Iterable, Optional

def _coerce_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def is_kalyan_game_day(date_value: Any) -> bool:
    """
    Returns True if Kalyan game runs on this date.
    Sunday = no game.
    """
    target = _coerce_date(date_value)
    return target.weekday() != 6   # Monday=0 ... Sunday=6


def find_last_game_row(rows: Iterable[Dict[str, Any]], date_key: str = "date") -> Optional[Dict[str, Any]]:
    """
    rows = iterable of dicts sorted by date ascending
    returns last row where game actually happened
    """
    rows_list = list(rows)
    for row in reversed(rows_list):
        if is_kalyan_game_day(row.get(date_key)):
            return row
    return None


def find_previous_game_row(
    rows: Iterable[Dict[str, Any]],
    before_date: Any,
    date_key: str = "date",
) -> Optional[Dict[str, Any]]:
    """
    returns last game day row strictly before before_date
    """
    target = _coerce_date(before_date)
    rows_list = list(rows)
    for row in reversed(rows_list):
        row_date = _coerce_date(row.get(date_key))
        if row_date < target and is_kalyan_game_day(row_date):
            return row
    return None
