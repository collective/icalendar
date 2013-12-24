import sys


if sys.version_info[0] == 2:  # pragma: no cover
    unicode_type = unicode
    bytes_type = str
    iteritems = lambda d, *args, **kwargs: iter(d.iteritems(*args, **kwargs))
else:  # pragma: no cover
    unicode_type = str
    bytes_type = bytes
    iteritems = lambda d, *args, **kwargs: iter(d.items(*args, **kwargs))
