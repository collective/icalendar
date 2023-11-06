#!/usr/bin/python3
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################
import atheris
import sys

with atheris.instrument_imports(
        include=['icalendar'],
        exclude=['pytz', 'six', 'site_packages', 'pkg_resources', 'dateutil']):
    import icalendar

_value_error_matches = [
    "component", "parse", "Expected", "Wrong date format", "END encountered",
    "vDDD", 'recurrence', 'Wrong datetime', 'Offset must', 'Invalid iCalendar'
]


def _fuzz_calendar(cal: icalendar.Calendar, should_walk: bool):
    if should_walk:
        for event in cal.walk('VEVENT'):
            event.to_ical()
    else:
        cal.to_ical()


@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    try:
        multiple = fdp.ConsumeBool()
        should_walk = fdp.ConsumeBool()

        cal = icalendar.Calendar.from_ical(fdp.ConsumeString(fdp.remaining_bytes()), multiple=multiple)

        if multiple:
            for c in cal:
                _fuzz_calendar(c, should_walk)
        else:
            _fuzz_calendar(cal, should_walk)
    except ValueError as e:
        if any(m in str(e) for m in _value_error_matches):
            return -1
        raise e


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()

