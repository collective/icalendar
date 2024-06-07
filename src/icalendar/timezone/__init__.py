"""This package contains all functionality for timezones."""
from .tzp import TZP

tzp = TZP()

def use_pytz():
    """Use pytz as the implementation that looks up and creates timezones."""
    tzp.use_pytz()

def use_zoneinfo():
    """Use zoneinfo as the implementation that looks up and creates timezones."""
    tzp.use_zoneinfo()

__all__ = ["tzp", "use_pytz", "use_zoneinfo"]
