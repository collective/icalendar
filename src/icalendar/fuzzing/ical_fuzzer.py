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


@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    try:
        b = fdp.ConsumeBool()

        cal = icalendar.Calendar.from_ical(fdp.ConsumeString(fdp.remaining_bytes()))

        if b:
            for event in cal.walk('VEVENT'):
                event.to_ical().decode('utf-8')
        else:
            cal.to_ical()
    except ValueError as e:
        if any(m in str(e) for m in _value_error_matches):
            return -1
        raise e


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
