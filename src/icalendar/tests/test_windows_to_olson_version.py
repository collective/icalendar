import re

from icalendar.timezone import windows_to_olson


def test_windows_to_olson_records_cldr_source_version():
    """The generated mapping identifies the exact CLDR source commit."""
    assert re.fullmatch(r"[0-9a-f]{40}", windows_to_olson.version)
    assert re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", windows_to_olson.version_date)
    documentation = windows_to_olson.__doc__
    assert documentation is not None
    assert f"cldr/blob/{windows_to_olson.version}/" in documentation
