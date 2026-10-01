"""This module contains compatibility code for different Python versions.

All compatibility checks and imports should go here.
This way, we can centralize the handling of different Python versions.

Do NOT import this module directly if you use icalendar.
Members will be added and removed without deprecation warnings.
"""

import functools
import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

try:
    from typing import Self
except ImportError:
    try:
        from typing_extensions import Self
    except ImportError:
        Self = "Self"

if TYPE_CHECKING:
    import sys
    from typing import TypeGuard

    if sys.version_info >= (3, 13):
        from typing import TypeIs
    else:
        from typing_extensions import TypeIs
    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self
else:
    # we cannot use a TypeGuard = "TypeGuard" hack since it's used with a parameter
    TypeGuard = TypeIs = Self = None


def deprecate_for_version_8(func: Callable[P, R]) -> Callable[P, R]:
    """Issue a warning for deprecated functions to be removed in version 8."""
    public_name = func.__name__.removeprefix("_")

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        warnings.warn(
            f"{public_name} is deprecated and will be removed in icalendar 8",
            DeprecationWarning,
            stacklevel=2,
        )
        wrapper.__name__ = public_name
        return func(*args, **kwargs)

    return wrapper


__all__ = [
    "Self",
    "TypeGuard",
    "TypeIs",
    "deprecate_for_version_8",
]
