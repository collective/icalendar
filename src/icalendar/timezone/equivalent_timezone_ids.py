"""This module helps identifying the timezone ids and where they differ.

The algorithm: We use the tzname and the utcoffset for each hour from
1970 - 2030.
We make a big map.
If they are equivalent, they are equivalent within the time that is mostly used.

You can regenerate the information from this module.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, tzinfo
from itertools import chain
from pprint import pprint
from zoneinfo import ZoneInfo, available_timezones


def main(start=datetime(1970, 1, 1), end=datetime(2030, 1, 1)):
    """Generate the module content."""
    dts = []
    dt = start
    while dt <= end:
        dts.append(dt)
        dt += timedelta(hours=1)

    def check(dt, tz:tzinfo):
        return (dt, tz.utcoffset(dt), tz.tzname(dt))
    def checks(tz:tzinfo) -> tuple:
        return tuple(check(dt, tz) for dt in dts)

    id2tzid = {}

    m = defaultdict(list) # checks -> tzids
    ids = list(sorted(available_timezones()))
    print("Press Control+C for partial computation.")
    tzs = list(map(ZoneInfo, ids))
    try:
        for i, tzid in enumerate(sorted(ids)):
            m[checks(tzs[i])].append(tzid)
            print(f"{i}/{len(ids)}")
    except KeyboardInterrupt:
        pass

    print("The following ids are equivalent")
    for ids in m.values():
        print(ids)


    def generate_count(ids_list:list[list]):
        """-> dt_id -> count"""
        counts = defaultdict(int)
        for ids in ids_list:
            for dt_id in ids:
                counts[dt_id] += 1
        return counts

    # we find identifying ids
    result = defaultdict(list)  # id -> tzids
    print("Calculating most identifying date ids")
    count = generate_count(m)
    look = [(set(k), v) for k, v in m.items()]
    ones = {k for k, v in count.items() if v == 1}
    print("Calculating best dates to check")
    date_count = defaultdict(int)
    for dt_id in ones:
        date_count[dt_id[0]] += 1
    best_dates = sorted(date_count, key=date_count.__getitem__)
    print("dates:")
    for date in reversed(best_dates):
        for tzid, tz in zip(ids, tzs):
            for 
    # while look:
    #         for tz in tzs:
    #             if  in ones:
                    
    #         for i, (k, tzids) in enumerate(look):
    #             if dt_id in k:
    #                 result[dt_id] = tzids
    #                 look.pop(i)
    #                 ones -= k
    #                 break
    #         break
    # print("Clearly identifying:")
    # pprint(result)



    # #
    # # If we always take those with the count close to half of them,
    # # we can create a binary decision tree.
    # #
    # def generate_tree(ids:list[list[list, list, list[str]]]):
    #     """Returns ((key), YES, NO)

    #     YES and NO are one of
    #     - (check, YES, NO)
    #     - [TZID]
    #     """
    #     print(f"generate_tree -> {len(m)}")
    #     if len(m) == 1:
    #         return m[list(m)[0]]
    #     half = len(m) / 2
    #     for dt_id, count in counts.items():
    #         if count == 1:
    #             ones.append(dt_id)
    #     # find count closest to half
    #     best_check = min(counts, key=lambda check: abs(counts[check] - half))
    #     yes = {}
    #     no = {}
    #     for cs, v in m.items():
    #         if best_check in cs:
    #             yes[cs] = v
    #         else:
    #             no[cs] = v
    #     return (
    #         best_check,
    #         generate_tree(yes),
    #         generate_tree(no)
    #     )

    # start = [] # [more than once, once, tzids]
    # counts = generate_count(m)
    # for ids, tzids in m.items():
    #     ones = []
    #     more = []
    #     for dt_id in ids:
    #         if counts[dt_id] == 1:
    #             ones.append(dt_id)
    #         else:
    #             more.append(dt_id)
    #         start.append([more, ones, tzids])

    tree = generate_tree(start, [])
    pprint(tree)

# def tzids_from_tzinfo(tzinfo: tzinfo) -> tuple[str]:
#     """Retrieve the timezone ids from the tzinfo object.

#     Some of them might be equivalent, some of them are not.
#     """
#     if hasattr(tzinfo, 'zone'):
#         return (tzinfo.zone,)  # pytz implementation
#     if hasattr(tzinfo, 'key'):
#         return (tzinfo.key,)  # ZoneInfo implementation
#     if not _tzname_to_tzid:
#         for tzid in :
#             _tzname_to_tzid[_identify_tzinfo(ZoneInfo(tzid))] += (tzid,)
#     return _tzname_to_tzid.get(_identify_tzinfo(tzinfo), ())



if __name__ == "__main__":
    main()