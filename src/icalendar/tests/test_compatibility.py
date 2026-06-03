"""Tests for compatibility helpers."""

import pytest

from icalendar.compatibility import deprecate_for_version_8


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
