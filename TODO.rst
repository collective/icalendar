TODO
====

- Update docs.

- Add a __add__ method to cal.Component, so that ``cal[key] = val`` works as
  expected. Currently, the value is added as is, but not converted to the
  correct subcomponent, as specified in prop.TypesFactory. See also the NOTE
  in: icalendar.tests.example.rst, Components, line 82.

- Eventually implement a ``decoded`` method for all icalendar.prop properties,
  so that cal.decoded doesn't call the from_ical methods but decode it into
  realy python natives. We want from_ical encode a ical string into a
  icalendar.prop instance, so decoding into a python native seems not to be
  appropriate there. (but the vDDD-types are encoded into python natives, so
  there is an inconsistence...)

OLD TODO's
==========

- Check and Fix VTIMEZONE component functionality and creating VTIMEZONE
  components from tzinfo instances.

- Automatic encoding and decoding of parameter values. Most of the
  work is done already. Just need to get it finished. Look at line 153
  in 'src/icalendar/parser.py'
