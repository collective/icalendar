"""This module contains compatibility code for different Python versions.

All compatibility checks and imports should go here.
This way, we can centralize the handling of different Python versions.

Do NOT import this module directly if you use icalendar.
Members will be added and removed without deprecation warnings.
"""

import warnings
from typing import TYPE_CHECKING


def deprecate_for_version_8(name: str) -> None:
    """Emit a DeprecationWarning for a function scheduled for removal in icalendar 8.

    Call this as the first statement inside a deprecated public wrapper function.
    ``stacklevel=3`` makes the warning point at the external caller's line, not at
    the wrapper or at this helper.

    Parameters:
        name: The public name of the deprecated function (e.g. ``"q_split"``).
    """
    warnings.warn(
        f"{name} is deprecated and will be removed in icalendar 8. "
        "If you are using this function externally, please contact the maintainers.",
        DeprecationWarning,
        stacklevel=3,
    )


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
