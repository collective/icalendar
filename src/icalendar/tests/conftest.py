try:
    from backports import zoneinfo  # type: ignore  # noqa: PGH003
except ImportError:
    import zoneinfo
from typing import Generator

import pytest

import icalendar

from . import timezone_ids

try:
    import pytz
except ImportError:
    pytz = None
import itertools
import sys
from pathlib import Path

from dateutil import tz

from icalendar.cal import Calendar, Component
from icalendar.timezone import TZP
from icalendar.timezone import tzp as _tzp

HAS_PYTZ = pytz is not None
if HAS_PYTZ:
    PYTZ_UTC = [
        pytz.utc,
        pytz.timezone("UTC"),
    ]
    PYTZ_IN_TIMEZONE = [
        lambda dt, tzname: pytz.timezone(tzname).localize(dt),
    ]
    PYTZ_TZP = ["pytz"]
else:
    PYTZ_UTC = []
    PYTZ_IN_TIMEZONE = []
    PYTZ_TZP = []


class DataSource:
    """A collection of parsed ICS elements (e.g calendars, timezones, events)"""

    def __init__(self, data_source_folder: Path, parser):
        self._parser = parser
        self._data_source_folder = data_source_folder

    def keys(self):
        """Return all the files that could be used."""
        return [
            p.stem
            for p in self._data_source_folder.iterdir()
            if p.suffix.lower() == ".ics"
        ]

    def __getitem__(self, attribute):
        """Parse a file and return the result stored in the attribute."""
        if attribute.endswith(".ics"):
            source_file = attribute
            attribute = attribute[:-4]
        else:
            source_file = attribute + ".ics"
        source_path = self._data_source_folder / source_file
        if not source_path.is_file():
            raise AttributeError(f"{source_path} does not exist.")
        with source_path.open("rb") as f:
            raw_ics = f.read()
        source = self._parser(raw_ics)
        if not isinstance(source, list):
            source.raw_ics = raw_ics
            source.source_file = source_file
        self.__dict__[attribute] = source
        return source

    def __contains__(self, key):
        """key in self.keys()"""
        if key.endswith(".ics"):
            key = key[:-4]
        return key in self.keys()

    def __getattr__(self, key):
        return self[key]

    def __repr__(self):
        return repr(self.__dict__)

    @property
    def multiple(self):
        """Return a list of all components parsed."""
        return self.__class__(
            self._data_source_folder, lambda data: self._parser(data, multiple=True)
        )


HERE = Path(__file__).parent
CALENDARS_FOLDER = HERE / "calendars"
TIMEZONES_FOLDER = HERE / "timezones"
EVENTS_FOLDER = HERE / "events"
ALARMS_FOLDER = HERE / "alarms"


@pytest.fixture(scope="module")
def calendars(tzp):
    return DataSource(CALENDARS_FOLDER, icalendar.Calendar.from_ical)


@pytest.fixture(scope="module")
def timezones(tzp):
    return DataSource(TIMEZONES_FOLDER, icalendar.Timezone.from_ical)


@pytest.fixture(scope="module")
def events(tzp):
    return DataSource(EVENTS_FOLDER, icalendar.Event.from_ical)


@pytest.fixture(scope="module")
def alarms(tzp):
    return DataSource(ALARMS_FOLDER, icalendar.Alarm.from_ical)


@pytest.fixture(params=PYTZ_UTC + [zoneinfo.ZoneInfo("UTC"), tz.UTC, tz.gettz("UTC")])
def utc(request, tzp):
    return request.param


@pytest.fixture(
    params=PYTZ_IN_TIMEZONE
    + [
        lambda dt, tzname: dt.replace(tzinfo=tz.gettz(tzname)),
        lambda dt, tzname: dt.replace(tzinfo=zoneinfo.ZoneInfo(tzname)),
    ]
)
def in_timezone(request, tzp):
    return request.param


# exclude broken calendars here
ICS_FILES_EXCLUDE = (
    "big_bad_calendar.ics",
    "issue_104_broken_calendar.ics",
    "small_bad_calendar.ics",
    "multiple_calendar_components.ics",
    "pr_480_summary_with_colon.ics",
    "parsing_error_in_UTC_offset.ics",
    "parsing_error.ics",
)
ICS_FILES = [
    file.name
    for file in itertools.chain(
        CALENDARS_FOLDER.iterdir(), TIMEZONES_FOLDER.iterdir(), EVENTS_FOLDER.iterdir()
    )
    if file.name not in ICS_FILES_EXCLUDE
]


@pytest.fixture(params=ICS_FILES)
def ics_file(tzp, calendars, timezones, events, request):
    """An example ICS file."""
    ics_file = request.param
    print("example file:", ics_file)
    for data in calendars, timezones, events:
        if ics_file in data:
            return data[ics_file]
    raise ValueError(f"Could not find file {ics_file}.")


FUZZ_V1 = [key for key in CALENDARS_FOLDER.iterdir() if "fuzz-testcase" in str(key)]


@pytest.fixture(params=FUZZ_V1)
def fuzz_v1_calendar(request):
    """Clusterfuzz calendars."""
    return request.param


@pytest.fixture
def x_sometime():
    """Map x_sometime to time"""
    icalendar.cal.types_factory.types_map["X-SOMETIME"] = "time"
    yield
    icalendar.cal.types_factory.types_map.pop("X-SOMETIME")


@pytest.fixture
def factory():
    """Return a new component factory."""
    return icalendar.ComponentFactory()


@pytest.fixture
def vUTCOffset_ignore_exceptions():
    icalendar.vUTCOffset.ignore_exceptions = True
    yield
    icalendar.vUTCOffset.ignore_exceptions = False


@pytest.fixture
def event_component(tzp):
    """Return an event component."""
    c = Component()
    c.name = "VEVENT"
    return c


@pytest.fixture
def c(tzp):
    """Return an empty component."""
    c = Component()
    return c


comp = c


@pytest.fixture
def calendar_component(tzp):
    """Return an empty component."""
    c = Component()
    c.name = "VCALENDAR"
    return c


@pytest.fixture
def filled_event_component(c, calendar_component):
    """Return an event with some values and add it to calendar_component."""
    e = Component(summary="A brief history of time")
    e.name = "VEVENT"
    e.add("dtend", "20000102T000000", encode=0)
    e.add("dtstart", "20000101T000000", encode=0)
    calendar_component.add_component(e)
    return e


@pytest.fixture()
def calendar_with_resources(tzp):
    c = Calendar()
    c["resources"] = 'Chair, Table, "Room: 42"'
    return c


@pytest.fixture(scope="module")
def tzp(tzp_name) -> Generator[TZP, None, None]:
    """The timezone provider."""
    _tzp.use(tzp_name)
    yield _tzp
    _tzp.use_default()


@pytest.fixture(params=PYTZ_TZP + ["zoneinfo"])
def other_tzp(request, tzp):
    """This is annother timezone provider.

    The purpose here is to cross test: pytz <-> zoneinfo.
    tzp as parameter makes sure we test the cross product.
    """
    return TZP(request.param)


@pytest.fixture
def pytz_only(tzp, tzp_name) -> str:
    """Skip tests that are not running under pytz."""
    assert tzp.uses_pytz()
    return tzp_name


@pytest.fixture
def zoneinfo_only(tzp, request, tzp_name) -> str:
    """Skip tests that are not running under zoneinfo."""
    assert tzp.uses_zoneinfo()
    return tzp_name


@pytest.fixture
def no_pytz(tzp_name) -> str:
    """Do not run tests with pytz."""
    assert tzp_name != "pytz"
    return tzp_name


@pytest.fixture
def no_zoneinfo(tzp_name) -> str:
    """Do not run tests with zoneinfo."""
    assert tzp_name != "zoneinfo"
    return tzp_name


def pytest_generate_tests(metafunc):
    """Parametrize without skipping:

    tzp_name will be parametrized according to the use of
    - pytz_only
    - zoneinfo_only
    - no_pytz
    - no_zoneinfo

    See https://docs.pytest.org/en/6.2.x/example/parametrize.html#deferring-the-setup-of-parametrized-resources
    """
    if "tzp_name" in metafunc.fixturenames:
        tzp_names = PYTZ_TZP + ["zoneinfo"]
        if "zoneinfo_only" in metafunc.fixturenames:
            tzp_names = ["zoneinfo"]
        if "pytz_only" in metafunc.fixturenames:
            tzp_names = PYTZ_TZP
        assert not (
            "zoneinfo_only" in metafunc.fixturenames
            and "pytz_only" in metafunc.fixturenames
        ), "Use pytz_only or zoneinfo_only but not both!"
        for name in ["pytz", "zoneinfo"]:
            if f"no_{name}" in metafunc.fixturenames and name in tzp_names:
                tzp_names.remove(name)
        metafunc.parametrize("tzp_name", tzp_names, scope="module")


class DoctestZoneInfo(zoneinfo.ZoneInfo):
    """Constent ZoneInfo representation for tests."""

    def __repr__(self):
        return f"ZoneInfo(key={self.key!r})"


def doctest_print(obj):
    """doctest print"""
    if isinstance(obj, bytes):
        obj = obj.decode("UTF-8")
    print(str(obj).strip().replace("\r\n", "\n").replace("\r", "\n"))


def doctest_import(name, *args, **kw):
    """Replace the import mechanism to skip the whole doctest if we import pytz."""
    if name == "pytz":
        return pytz
    return __import__(name, *args, **kw)


@pytest.fixture
def env_for_doctest(monkeypatch):
    """Modify the environment to make doctests run."""
    monkeypatch.setitem(sys.modules, "zoneinfo", zoneinfo)
    monkeypatch.setattr(zoneinfo, "ZoneInfo", DoctestZoneInfo)
    from icalendar.timezone.zoneinfo import ZONEINFO

    monkeypatch.setattr(ZONEINFO, "utc", zoneinfo.ZoneInfo("UTC"))
    return {"print": doctest_print}


@pytest.fixture(params=timezone_ids.TZIDS)
def tzid(request: pytest.FixtureRequest) -> str:
    """Return a timezone id to be used with pytz or zoneinfo.

    This goes through all the different timezones possible.
    """
    return request.param
