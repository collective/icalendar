import sys


if sys.version_info[0] == 2:
    unicode_type = unicode
    bytes_type = str
else:
    unicode_type = str
    bytes_type = bytes
