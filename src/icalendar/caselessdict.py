# -*- coding: utf-8 -*-
from icalendar import DEFAULT_ENCODING

def canonsort_keys(keys, canonical_order=None):
    """Sorts leading keys according to canonical_order.  Keys not specified in
    canonical_order will appear alphabetically at the end.

    """
    canonical_map = dict((k, i) for i, k in enumerate(canonical_order or []))
    head = [k for k in keys if k in canonical_map]
    tail = [k for k in keys if k not in canonical_map]
    return sorted(head, key=lambda k: canonical_map[k]) + sorted(tail)


def canonsort_items(dict1, canonical_order=None):
    """Returns a list of items from dict1, sorted by canonical_order.

    """
    return [(k, dict1[k]) for \
            k in canonsort_keys(dict1.keys(), canonical_order)]


class CaselessDict(dict):
    """A dictionary that isn't case sensitive, and only uses strings as keys.
    Values retain their case.

    """

    def __init__(self, *args, **kwargs):
        "Set keys to upper for initial dict"
        dict.__init__(self, *args, **kwargs)
        for k, v in self.items():
            k_upper = k.upper()
            if k != k_upper:
                dict.__delitem__(self, k)
                self[k_upper] = v

    def __getitem__(self, key):
        return dict.__getitem__(self, key.upper())

    def __setitem__(self, key, value):
        dict.__setitem__(self, key.upper(), value)

    def __delitem__(self, key):
        dict.__delitem__(self, key.upper())

    def __contains__(self, key):
        return dict.__contains__(self, key.upper())

    def get(self, key, default=None):
        return dict.get(self, key.upper(), default)

    def setdefault(self, key, value=None):
        return dict.setdefault(self, key.upper(), value)

    def pop(self, key, default=None):
        return dict.pop(self, key.upper(), default)

    def popitem(self):
        return dict.popitem(self)

    def has_key(self, key):
        return dict.__contains__(self, key.upper())

    def update(self, indict):
        """
        Multiple keys where key1.upper() == key2.upper() will be lost.
        """
        for entry in indict:
            self[entry] = indict[entry]

    def copy(self):
        return CaselessDict(dict.copy(self))

    def clear(self):
        dict.clear(self)

    def __repr__(self):
        # TODO: not necessary when to_ical also outs unicode
        dict_repr = dict(map(
            lambda item: (item[0].encode(DEFAULT_ENCODING), item[1]),
            self.iteritems()
            ))
        return 'CaselessDict(%s)' % dict_repr

    # A list of keys that must appear first in sorted_keys and sorted_items;
    # must be uppercase.
    canonical_order = None

    def sorted_keys(self):
        """
        Sorts keys according to the canonical_order for the derived class.
        Keys not specified in canonical_order will appear at the end.
        """
        return canonsort_keys(self.keys(), self.canonical_order)

    def sorted_items(self):
        """
        Sorts items according to the canonical_order for the derived class.
        Items not specified in canonical_order will appear at the end.
        """
        return canonsort_items(self, self.canonical_order)
