from .provider import Provider
from datetime import datetime

class TZP(Provider):
    """This is the timezone provider proxy.

    If you would like to have another timezone implementation,
    you can create a new one and pass it to this proxy.
    All of icalendar will then use this timezone implementation.
    """

    def __init__(self):
        """Create a new timezone implementation proxy."""
        self.use_pytz()

    def use_pytz(self):
        """Use pytz as the timezone provider."""
        from .pytz import PYTZ
        self.use(PYTZ())

    def use(self, provider: Provider):
        """Use another timezone implementation."""
        self.__provider = provider

    def make_utc(self, value: datetime):
        """Convert a datetime object to use UTC.

        If there is no timezone, UTC is assumed.
        """
        return self.__provider.make_utc(value)


__all__ = ["TZP"]
