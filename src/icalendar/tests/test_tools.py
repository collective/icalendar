from icalendar.tools import normalize_pytz
from datetime import datetime
import pytz

def test_normalize_pytz():
    tz = pytz.timezone("Europe/London")
    pytz_dt = tz.localize(datetime(2024, 1, 1, 10, 0, 0))
    result = normalize_pytz(pytz_dt)
    assert result.tzinfo == pytz_dt.tzinfo
