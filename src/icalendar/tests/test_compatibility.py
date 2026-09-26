"""Tests for compatibility helpers."""

import sys
from typing import get_type_hints

import pytest

from icalendar import vBoolean
from icalendar.compatibility import deprecate_for_version_8

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@pytest.mark.parametrize(
    ("method", "return_type"),
    [(vBoolean.examples, list[Self]), (vBoolean.from_jcal, Self)],
)
def test_self_return_type_is_preserved(method, return_type):
    """Runtime annotations should retain Self for API documentation."""
    assert get_type_hints(method)["return"] == return_type


def test_deprecate_for_version_8_warns_and_delegates() -> None:
    """The wrapper should warn while preserving the wrapped behavior."""

    def _join_parts(left: str, right: str = "") -> str:
        return f"{left}-{right}"

    deprecated = deprecate_for_version_8(_join_parts)

    with pytest.warns(
        DeprecationWarning,
        match="join_parts is deprecated and will be removed in icalendar 8",
    ):
        assert deprecated("left", right="right") == "left-right"

    assert deprecated.__name__ == "join_parts"
