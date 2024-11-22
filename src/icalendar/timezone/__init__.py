"""This package contains all functionality for timezones."""
from .tzid import tzid_from_dt, tzid_from_tzinfo, tzids_from_tzinfo
from .tzp import TZP

tzp = TZP()

def use_pytz():
    """Use pytz as the implementation that looks up and creates timezones."""
    tzp.use_pytz()


def use_zoneinfo():
    """Use zoneinfo as the implementation that looks up and creates timezones."""
    tzp.use_zoneinfo()

__all__ = [
    "TZP",
    "tzp",
    "use_pytz",
    "use_zoneinfo",
    "tzid_from_tzinfo",
    "tzid_from_dt",
    "tzids_from_tzinfo"
]
