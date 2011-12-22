# -*- coding: latin-1 -*-

def canonsort(keys, canonical_order=None):
    """
    Sorts leading keys according to canonical_order.
    Keys not specified in canonical_order will appear alphabetically at the end.
    Keys are expected to be uppercase.

    >>> keys = ['DTEND', 'DTSTAMP', 'DTSTART', 'UID', 'SUMMARY', 'LOCATION']
    >>> canonsort(keys)
    ['DTEND', 'DTSTAMP', 'DTSTART', 'LOCATION', 'SUMMARY', 'UID']
    >>> canonsort(keys, ('SUMMARY', 'DTSTART', 'DTEND', ))
    ['SUMMARY', 'DTSTART', 'DTEND', 'DTSTAMP', 'LOCATION', 'UID']
    >>> canonsort(keys, ('UID', 'DTSTART', 'DTEND', ))
    ['UID', 'DTSTART', 'DTEND', 'DTSTAMP', 'LOCATION', 'SUMMARY']
    >>> canonsort(keys, ('UID', 'DTSTART', 'DTEND', 'RRULE', 'EXDATE'))
    ['UID', 'DTSTART', 'DTEND', 'DTSTAMP', 'LOCATION', 'SUMMARY']
    """
    canonical_map = dict((k.upper(), i) for i, k in enumerate(canonical_order or []))
    head = [k for k in keys if k in canonical_map]
    tail = [k for k in keys if k not in canonical_map]
    return sorted(head, key=lambda k: canonical_map[k])  +  sorted(tail)

class CaselessDict(dict):
    """
    A dictionary that isn't case sensitive, and only use string as keys.

    >>> ncd = CaselessDict(key1='val1', key2='val2')
    >>> ncd
    CaselessDict({'KEY2': 'val2', 'KEY1': 'val1'})
    >>> ncd['key1']
    'val1'
    >>> ncd['KEY1']
    'val1'
    >>> ncd['KEY3'] = 'val3'
    >>> ncd['key3']
    'val3'
    >>> ncd.setdefault('key3', 'FOUND')
    'val3'
    >>> ncd.setdefault('key4', 'NOT FOUND')
    'NOT FOUND'
    >>> ncd['key4']
    'NOT FOUND'
    >>> ncd.get('key1')
    'val1'
    >>> ncd.get('key3', 'NOT FOUND')
    'val3'
    >>> ncd.get('key4', 'NOT FOUND')
    'NOT FOUND'
    >>> 'key4' in ncd
    True
    >>> del ncd['key4']
    >>> ncd.has_key('key4')
    False
    >>> ncd.update({'key5':'val5', 'KEY6':'val6', 'KEY5':'val7'})
    >>> ncd['key6']
    'val6'
    >>> keys = ncd.keys()
    >>> keys.sort()
    >>> keys
    ['KEY1', 'KEY2', 'KEY3', 'KEY5', 'KEY6']
    """

    def __init__(self, *args, **kwargs):
        "Set keys to upper for initial dict"
        dict.__init__(self, *args, **kwargs)
        for k,v in self.items():
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

    def __contains__(self, item):
        return dict.__contains__(self, item.upper())

    def get(self, key, default=None):
        return dict.get(self, key.upper(), default)

    def setdefault(self, key, value=None):
        return dict.setdefault(self, key.upper(), value)

    def pop(self, key, default=None):
        return dict.pop(self, key.upper(), default)

    def popitem(self):
        return dict.popitem(self)

    def has_key(self, key):
        return dict.has_key(self, key.upper())

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
        return 'CaselessDict(' + dict.__repr__(self) + ')'

    canonical_order = None

    def sorted_keys(self):
        """
        Sorts keys according to the canonical_order for the derived class.
        Keys not specified in canonical_order will appear at the end.
        """
        return canonsort(self.keys(), self.canonical_order)
