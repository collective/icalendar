from typing import List, Union

SEQUENCE_TYPES = (list, tuple)
DEFAULT_ENCODING = 'utf-8'
ICAL_TYPE = Union[str, bytes]


def from_unicode(value: ICAL_TYPE, encoding='utf-8') -> bytes:
    """
    Converts a value to bytes, even if it already is bytes
    :param value: The value to convert
    :param encoding: The encoding to use in the conversion
    :return: The bytes representation of the value
    """
    if isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        try:
            return value.encode(encoding)
        except UnicodeEncodeError:
            return value.encode('utf-8', 'replace')
    else:
        return value


def to_unicode(value: ICAL_TYPE, encoding='utf-8-sig') -> str:
    """Converts a value to unicode, even if it is already a unicode string.
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, bytes):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            return value.decode('utf-8-sig', 'replace')
    else:
        return value


def data_encode(
        data: Union[ICAL_TYPE, dict, list], encoding=DEFAULT_ENCODING
) -> Union[bytes, List[bytes], dict]:
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


__all__ = ["DEFAULT_ENCODING", "SEQUENCE_TYPES", "ICAL_TYPE", "data_encode", "from_unicode",
           "to_unicode"]
