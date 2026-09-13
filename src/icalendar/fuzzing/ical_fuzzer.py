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
import base64
import contextlib
import sys

import atheris

with atheris.instrument_imports():
    import icalendar.cal.calendar
    from icalendar.tests.fuzzed import fuzz_v1_calendar


@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    multiple = fdp.ConsumeBool()
    should_walk = fdp.ConsumeBool()
    calendar_string = fdp.ConsumeString(fdp.remaining_bytes())
    print("--- start calendar ---")
    with contextlib.suppress(UnicodeEncodeError):
        # print the ICS file for the test case extraction
        # see https://stackoverflow.com/a/27367173/1320237
        print(
            base64.b64encode(calendar_string.encode("UTF-8", "surrogateescape")).decode(
                "ASCII"
            )
        )

    fuzz_v1_calendar(
        icalendar.cal.calendar.Calendar.from_ical,
        calendar_string,
        multiple,
        should_walk,
    )
    print("--- end calendar ---")


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
