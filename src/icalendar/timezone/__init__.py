"""This package contains all functionality for timezones."""
from .tzp import TZP

tzp = TZP()
tzp.use_pytz()

__all__ = ["tzp"]
