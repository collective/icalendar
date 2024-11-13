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
from typing import Callable

from zoneinfo import ZoneInfo, available_timezones


def check(dt, tz:tzinfo):
    return (dt, tz.utcoffset(dt), tz.tzname(dt))

def checks(tz:tzinfo) -> tuple:
    result = []
    for dt in DTS:
        with contextlib.suppress(Exception):
            result.append(check(dt, tz))
    return result

START = datetime(1970, 1, 1)  # noqa: DTZ001
END = datetime(2030, 1, 1)  # noqa: DTZ001

DTS = []
dt = START
while dt <= END:
    DTS.append(dt)
    dt += timedelta(hours=1)
del dt

def main(
        create_timezones:list[Callable[[str], tzinfo]],
    ):
    """Generate a lookup table for timezone information if unknown timezones.

    
    """
    id2tzid = {}

    dtids2tzids = defaultdict(tuple) # checks -> tzids
    # tzids without timezones that change
    tzids = [
        tzid for tzid in sorted(available_timezones())
        if tzid.lower() not in ("factory", "localtime")
    ]
    print("Press Control+C for partial computation.")
    write_to_result_file = True
    
    try:
        start = time()
        pool_size = cpu_count()
        pool = Pool(pool_size)
        iter = enumerate(sorted(tzids))
        for i, tzid in iter:
            this_go_tzids = [tzid]
            for j, tzid in iter:
                this_go_tzids.append(tzid)
                if len(this_go_tzids) >= pool_size:
                    break
            i=j
            for create_timezone in create_timezones:
                try:
                    tz = create_timezone(tzid)
                except Exception as e:
                    print(e)
                    continue
                tzid_checks = pool.map(checks, this_go_tzids)
                for tzid_check in tzid_checks:
                    dtids2tzids[tuple(tzid_check)] += (tzid,)
            duration = time() - start
            print(f"{i+1}/{len(tzids)}, {timedelta(seconds=int(duration * len(tzids) / (i+1) - duration))} remaining.")
    except KeyboardInterrupt:
        write_to_result_file = False
        pass

    print("The following ids are equivalent")
    for tzids in dtids2tzids.values():
        print(tzids)


    # def generate_count(ids_list:list[list]):
    #     """-> dt_id -> count"""
    #     counts = defaultdict(int)
    #     for ids in ids_list:
    #         for dt_id in ids:
    #             counts[dt_id] += 1
    #     return counts

    print("counting tzids for dtids")
    # datetime -> dtid -> tzids
    dates : list[datetime] = []
    lookup :dict[datetime, dict[tuple, list[str]]]= defaultdict(dict)
    tzids2dtids : dict[tuple, tuple] = {
        v:k for k, v in dtids2tzids.items()
    }
    # uniquedtid2tzids = dtid -> [tzids, ...]
    n = len(dtids2tzids)
    uniquedtid2tzids : dict[tuple, list[tuple|str]] = defaultdict(list)
    for i, (dtids, tzids) in enumerate(dtids2tzids.items()):
        for dtid in dtids:
            uniquedtid2tzids[dtid].append(tzids)
        print(f"{i+1}/{n}")
    print("finding identifying ids")
    n = len(uniquedtid2tzids.items())
    p = 0
    for i, (dtid, tzids) in enumerate(list(uniquedtid2tzids.items())):
        if len(tzids) == 1:
            uniquedtid2tzids[dtid] = tzids[0]
        else:
            del uniquedtid2tzids[dtid]
        p_ = int((i+1)/n*100)
        if p_ != p:
            p = p_
            print(f"{p}%")
    # uniquedtid2tzids = dtid -> tuple[tzids]
    dt2uniquedtids = defaultdict(set)
    for dtid in uniquedtid2tzids:
        dt2uniquedtids[dtid[0]].add(dtid)

    print("Computing tree to find tzids")
    n = len(dt2uniquedtids)
    p = 0
    while dt2uniquedtids:
        dt = min(dt2uniquedtids)
        uniquedtids = dt2uniquedtids.pop(dt)
        dates.append(dt)
        for uniquedtid in uniquedtids:
            tzids = uniquedtid2tzids[uniquedtid]
            lookup[dt][uniquedtid[1:]] = tzids
            for dtid in tzids2dtids[tzids]:
                dtids_to_shrink = dt2uniquedtids[dtid[0]]
                dtids_to_shrink-= {dtid}
                if not dtids_to_shrink:
                    del dt2uniquedtids[dtid[0]]
        p_ = int(100 - len(dt2uniquedtids)/n*100)
        if p_ != p:
            p = p_
            print(f"{p}%")

    file = Path(__file__).parent / "equivalent_timezone_ids_result.py"
    print(f"The result is written to {file}.")
    lookup = dict(lookup)
    print("lookup = ", end="")
    pprint(lookup)
    if write_to_result_file:
        with file.open("w") as f:
            f.write(f"'''This file is automatically generated by {Path(__file__).name}'''\n")
            f.write("import datetime\n\n")
            f.write(f"lookup = ")
            pprint(lookup, stream=f)
            f.write("\n\n__all__ = ['lookup']\n")

    return lookup

def tzinfo2tzids(tzinfo: tzinfo) -> tuple[str]:
    """We return the tzids for a certain tzinfo object.

    With different datetimes, we match
    (tzinfo.utcoffset(dt), tzinfo.tzname(dt))

    If we could identify the timezone, you will receive a tuple
    with at least one tzid. All tzids are equivalent which means
    that they describe the same timezone.

    You should get results with any timezone implementation if it is known.
    This one is especially useful for dateutil.

    In the following example, we can see that the timezone Africa/Accra
    is equivalent to many others.

    >>> import zoneinfo
    >>> from icalendar.timezone.equivalent_timezone_ids import tzinfo2tzids
    >>> tzinfo2tzids(zoneinfo.ZoneInfo("Africa/Accra"))
    ('Africa/Abidjan', 'Africa/Accra', 'Africa/Bamako', 'Africa/Banjul', 'Africa/Conakry', 'Africa/Dakar')
    """
    from icalendar.timezone.equivalent_timezone_ids_result import lookup

    for dt in sorted(lookup):
        _, utcoffset, tzname = check(dt, tzinfo)
        tzids = lookup[dt].get((utcoffset, tzname), ())
        if tzids:
            return tzids
    return ()


__all__ = ["main", "tzinfo2tzids"]

if __name__ == "__main__":
    from dateutil.tz import gettz
    from pytz import timezone
    from zoneinfo import ZoneInfo
    main([ZoneInfo, gettz, timezone])
