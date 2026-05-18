"""This module contains compatibility code for different Python versions.

All compatibility checks and imports should go here.
This way, we can centralize the handling of different Python versions.

Do NOT import this module directly if you use icalendar.
Members will be added and removed without deprecation warnings.
"""

import functools
import warnings
from typing import TYPE_CHECKING


def deprecate_for_version_8(func):
    """Return a deprecated public alias for *func*.

    Wraps *func* so that every call emits a :exc:`DeprecationWarning` and
    then delegates to the original implementation.  The public name used in
    the warning message is derived from ``func.__name__`` by stripping a
    leading underscore.

    Use like this::

        def _q_join(...):
            \"\"\"docstring...\"\"\"
            ...

        q_join = deprecate_for_version_8(_q_join)

    Parameters:
        func: The private implementation to wrap.

    Returns:
        A wrapper with the same signature and docstring as *func* that emits
        a :exc:`DeprecationWarning` on every call.
    """
    public_name = func.__name__.lstrip("_")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"{public_name} is deprecated and will be removed in icalendar 8. "
            "If you are using this function externally, "
            "please contact the maintainers.",
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper


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

__all__ = [
    "Self",
    "TypeGuard",
    "TypeIs",
    "deprecate_for_version_8",
]
