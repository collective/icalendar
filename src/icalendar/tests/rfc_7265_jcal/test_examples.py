"""Tests for jcal running on all ics files."""

import json


def test_to_jcal_can_be_json_serialized(ics_file):
    """Check that all calendars can be converted to JCAL and serialized to JSON."""
    jcal = ics_file.to_jcal()
    s = json.dumps(jcal)
    assert s
