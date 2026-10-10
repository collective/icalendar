"""SKIP accessor for vRecur.

Registered from the package init so ``vRecur.skip`` is available wherever
the recur types are imported.
"""

from icalendar.error import InvalidCalendar
from icalendar.parser_tools import SEQUENCE_TYPES
from icalendar.prop.recur.recur import vRecur
from icalendar.prop.recur.skip import vSkip


def _get_skip(self) -> vSkip | None:
    """The SKIP part of the recurrence rule.

    SKIP is defined by :rfc:`7529` and selects how a recurrence instance
    that falls on an invalid date is handled after RSCALE is applied.
    Valid values are ``OMIT`` (the default in the RFC), ``FORWARD``, and
    ``BACKWARD``.

    Because only one value is expected, if multiple values are present,
    the first one is returned. If the value is missing or an empty
    sequence, ``None`` is returned.

    Setting this to ``None`` deletes the value, as does ``del``.

    Raises:
        InvalidCalendar: if a value cannot be read or set as a skip value.
        TypeError: when setting a value that is not a skip string
            or :class:`~icalendar.prop.recur.skip.vSkip`.

    Example:
        ..  code-block:: pycon

            >>> from icalendar.prop import vRecur
            >>> vRecur("FREQ=YEARLY;SKIP=FORWARD").skip == "FORWARD"
            True
            >>> vRecur("FREQ=YEARLY").skip is None
            True
    """
    values = self.get("SKIP")
    if values is None or (isinstance(values, SEQUENCE_TYPES) and len(values) == 0):
        return None
    value = values[0] if isinstance(values, SEQUENCE_TYPES) else values
    if isinstance(value, vSkip):
        return value
    try:
        return vSkip(value)
    except (TypeError, ValueError) as e:
        raise InvalidCalendar("SKIP must be OMIT, FORWARD, or BACKWARD") from e


def _set_skip(self, value: str | vSkip | None) -> None:
    """Set the SKIP part of the recurrence rule, or delete it if None."""
    if value is None:
        del self.skip
        return
    if not isinstance(value, (str, vSkip)):
        raise TypeError(f"skip must be a skip string or vSkip, got {value!r}")
    try:
        skip = vSkip(value)
    except (TypeError, ValueError) as e:
        raise InvalidCalendar("SKIP must be OMIT, FORWARD, or BACKWARD") from e
    # from_ical stores SKIP as a one-item list via parse_type; keep
    # that representation so assignment matches a parsed vRecur.
    self["SKIP"] = [skip]


def _del_skip(self) -> None:
    """Delete the SKIP part of the recurrence rule."""
    self.pop("SKIP", None)


vRecur.skip = property(_get_skip, _set_skip, _del_skip)
