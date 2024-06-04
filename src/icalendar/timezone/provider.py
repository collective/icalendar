"""This is an abstract class that provides timezomes."""
from abc import ABC, abstractmethod

class Provider(ABC):
    """Provide a timezone implementation."""

    @abstractmethod
    def make_utc(self, datetime):
        pass
