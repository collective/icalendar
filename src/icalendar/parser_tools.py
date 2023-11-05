from typing import Any

SEQUENCE_TYPES = (list, tuple)
DEFAULT_ENCODING = 'utf-8'


def from_unicode(value: Any, encoding='utf-8') -> bytes:
    """
    Converts a value to bytes, even if it already is bytes
    :param value: The value to convert
    :param encoding: The encoding to use in the conversion
    :return: The bytes representation of the value
    """
    if isinstance(value, bytes):
        value = value
    elif isinstance(value, str):
        try:
            value = value.encode(encoding)
        except UnicodeEncodeError:
            value = value.encode('utf-8', 'replace')
    return value


def to_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even if it is already a unicode string.
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, bytes):
        try:
            value = value.decode(encoding)
        except UnicodeDecodeError:
            value = value.decode('utf-8', 'replace')
    return value


def data_encode(data, encoding=DEFAULT_ENCODING):
    """Encode all datastructures to the given encoding.
    Currently unicode strings, dicts and lists are supported.
    """
    # https://stackoverflow.com/questions/1254454/fastest-way-to-convert-a-dicts-keys-values-from-unicode-to-str
    if isinstance(data, str):
        return data.encode(encoding)
    elif isinstance(data, dict):
        return dict(map(data_encode, iter(data.items())))
    elif isinstance(data, list) or isinstance(data, tuple):
        return list(map(data_encode, data))
    else:
        return data
