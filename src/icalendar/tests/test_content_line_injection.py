"""Content lines must reject unescaped newlines, even under ``python -O``.

A newline in a content line folds into an *injected* content line (and can forge
whole components), so it must be rejected. The check used to be an ``assert``,
which Python removes under ``-O`` / ``PYTHONOPTIMIZE`` -- silently disabling the
protection. These tests pin the behaviour in both normal and optimized mode.
"""

import subprocess
import sys

import pytest

from icalendar import Event
from icalendar.parser import Contentline


def test_contentline_rejects_newline():
    """A newline in a content line raises ValueError (not AssertionError)."""
    with pytest.raises(ValueError):
        Contentline(b"1234\r\n\r\n1234")


def test_property_name_with_newline_is_rejected():
    """A crafted property name cannot inject extra content lines via to_ical."""
    event = Event()
    event.add("X-A\r\nX-INJECTED;ROLE=CHAIR", "value")
    with pytest.raises(ValueError):
        event.to_ical()


def _run_optimized(code: str) -> subprocess.CompletedProcess:
    # Trusted input: our own interpreter running a fixed snippet, no shell.
    return subprocess.run(  # noqa: S603
        [sys.executable, "-O", "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )


def test_newline_guard_survives_python_O_optimization():
    """The guard must hold under ``python -O``, where ``assert`` is stripped.

    Run in a subprocess because ``-O`` only affects bytecode compiled by that
    interpreter, not the already-imported test module.
    """
    code = (
        "from icalendar import Event\n"
        "ev = Event()\n"
        "ev.add('X-A\\r\\nX-INJECTED;ROLE=CHAIR', 'value')\n"
        "try:\n"
        "    out = ev.to_ical()\n"
        "except ValueError:\n"
        "    print('REJECTED')\n"
        "else:\n"
        "    print('INJECTED' if b'X-INJECTED' in out else 'CLEAN')\n"
    )
    result = _run_optimized(code)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "REJECTED", result.stdout
