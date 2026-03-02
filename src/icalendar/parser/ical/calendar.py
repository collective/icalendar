"""Special parsing for calendar components."""

from .component import ComponentIcalParser


class CalendarIcalParser(ComponentIcalParser):
    """A parser for calendar components."""

    def prepare_components(self) -> None:
        """Prepare the parsed components.

        This handles timezone forward references.
        """
        all_timezones_so_far = True
        for comp in self._components:
            for component in comp.subcomponents:
                if component.name == "VTIMEZONE":
                    if not all_timezones_so_far:
                        # If a preceding component refers to a VTIMEZONE defined
                        # later in the source st
                        # (forward references are allowed by RFC 5545), then the
                        # earlier component may have
                        # the wrong timezone attached.
                        # However, during computation of comps, all VTIMEZONEs
                        # observed do end up in
                        # the timezone cache. So simply re-running from_ical will
                        # rely on the cache
                        # for those forward references to produce the correct result.
                        # See test_create_america_new_york_forward_reference.
                        self.initialize_parsing()
                        self.parse_content_lines()
                        return
                else:
                    all_timezones_so_far = False


__all__ = ["CalendarIcalParser"]
