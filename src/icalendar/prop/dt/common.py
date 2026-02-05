"""Common functionality for time based property types."""

from datetime import date, datetime, time, timedelta
from typing import TypeAlias

DT_TYPE: TypeAlias = (
    datetime
    | date
    | timedelta
    | time
    | tuple[datetime, datetime]
    | tuple[datetime, timedelta]
)

__all__ = ["DT_TYPE"]
