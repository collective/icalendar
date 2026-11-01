from datetime import datetime

from icalendar.tools import normalize_pytz


def test_normalize_pytz(pytz_only):
    import pytz

    tz = pytz.timezone("Europe/London")
    pytz_dt = tz.localize(datetime(2024, 1, 1, 10, 0, 0))
    result = normalize_pytz(pytz_dt)
    assert result.tzinfo == pytz_dt.tzinfo
