"""This module contains compatibility code for older Python versions."""

import sys
from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    if sys.version_info >= (3, 10):
        from typing import TypeGuard
    else:
        from typing_extensions import TypeGuard

    if sys.version_info >= (3, 13):
        from typing import TypeIs
    else:
        from typing_extensions import TypeIs
else:
    # we cannot use a TypeGuard = "TypeGuard" hack since it's used with a parameter
    TypeGuard = TypeIs = None

__all__ = [
    "Self",
    "TypeIs",
    "TypeGuard",
    "ZoneInfo",
    "zoneinfo",
]
