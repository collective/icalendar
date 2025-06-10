"""This module contains compatibility code for older Python versions."""


try:
    from typing import Self
except ImportError:
    try:
        from typing_extensions import Self
    except ImportError:
        Self = "Self"

try:
    import zoneinfo
except ImportError:
    import backports.zoneinfo as zoneinfo

ZoneInfo = zoneinfo.ZoneInfo

__all__ = [
    "Self",
    "ZoneInfo",
    "zoneinfo",
]
