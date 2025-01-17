"""This module helps identifying the timezone ids and where they differ.

The algorithm: We use the tzname and the utcoffset for each hour from
1970 - 2030.
We make a big map.
If they are equivalent, they are equivalent within the time that is mostly used.

You can regenerate the information from this module.

See also:
- https://stackoverflow.com/questions/79185519/which-timezones-are-equivalent

"""
from __future__ import annotations

import contextlib
from collections import defaultdict
from datetime import datetime, timedelta, tzinfo
from multiprocessing import Pool, cpu_count
from pathlib import Path
from pprint import pprint
from time import time
from typing import Callable, NamedTuple, Optional, Any, Tuple, List

from zoneinfo import ZoneInfo, available_timezones

from pytz import AmbiguousTimeError, NonExistentTimeError


def check(dt, tz:tzinfo):
    return (dt, tz.utcoffset(dt))

def checks(tz:tzinfo) -> List[Tuple[Any, Optional[timedelta]]]:
    result = []
    for dt in DTS:
        try:
            result.append(check(dt, tz))
        except Exception as e:
            print(e)
    return result


START = datetime(1970, 1, 1)  # noqa: DTZ001
END = datetime(2000, 1, 1)  # noqa: DTZ001

DTS = []
dt = START
while dt <= END:
    DTS.append(dt)
    dt += timedelta(hours=25) # This must be big enough to be fast and small enough to identify the timeszones before it is the present year
del dt

def main(
        create_timezones:list[Callable[[str], tzinfo]],
        name:str,
        pool_size = cpu_count()
    ):
    """Generate a lookup table for timezone information if unknown timezones.

    We cannot create one lookup for all because they seem to be all equivalent
    if we mix timezone implementations.
    """
    print(create_timezones, name)
    unsorted_tzids = available_timezones()
    unsorted_tzids.remove("localtime")
    unsorted_tzids.remove("Factory")
    
    class TZ(NamedTuple):
        tz: tzinfo
        id:str

    tzs = [
        TZ(create_timezone(tzid), tzid)
        for create_timezone in create_timezones
        for tzid in unsorted_tzids
    ]
    
    def generate_tree(
            tzs: list[TZ],
            step:timedelta=timedelta(hours=1),
            start:datetime=START,
            end:datetime=END,
            todo:Optional[set[str]]=None
        ) -> tuple[datetime, dict[timedelta, set[str]]] | set[str]:  # should be recursive
        """Generate a lookup tree."""
        if todo is None:
            todo = [tz.id for tz in tzs]
        print(f"{len(todo)} left to compute")
        print(len(tzs))
        if len(tzs) == 0:
            raise ValueError("tzs cannot be empty")
        if len(tzs) == 1:
            todo.remove(tzs[0].id)
            return {tzs[0].id}
        while start < end:
            offsets : dict[timedelta, list[TZ]] = defaultdict(list)
            try:
                for tz in tzs:
                    offsets[tz.tz.utcoffset(start)].append(tz)
            except (NonExistentTimeError, AmbiguousTimeError):
                start += step
                continue
            if len(offsets) == 1:
                start += step
                continue
            lookup = {}
            for offset, tzs in offsets.items():
                lookup[offset] = generate_tree(tzs=tzs, step=step, start=start + step, end=end, todo=todo)
            return start, lookup
        result = set()
        for tz in tzs:
            result.add(tz.id)
            todo.remove(tz.id)
        return result


    lookup = generate_tree(tzs, step=timedelta(hours=33))

    file = Path(__file__).parent / f"equivalent_timezone_ids_{name}.py"
    print(f"The result is written to {file}.")
    print("lookup = ", end="")
    pprint(lookup)
    with file.open("w") as f:
        f.write(f"'''This file is automatically generated by {Path(__file__).name}'''\n")
        f.write("import datetime\n\n")
        f.write("\nlookup = ")
        pprint(lookup, stream=f)
        f.write("\n\n__all__ = ['lookup']\n")

    return lookup

__all__ = ["main"]

if __name__ == "__main__":
    from dateutil.tz import gettz
    from pytz import timezone
    from zoneinfo import ZoneInfo
    # add more timezone implementations if you like
    main([ZoneInfo, timezone, gettz], "result",
         pool_size=1
    )
