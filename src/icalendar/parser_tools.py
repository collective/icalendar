from typing import List, Union

SEQUENCE_TYPES = (list, tuple)
DEFAULT_ENCODING = "utf-8"
ICAL_TYPE = Union[str, bytes]


def _from_unicode(value: ICAL_TYPE, encoding="utf-8") -> bytes:
    """Converts a value to bytes, even if it is already bytes.

    Parameters:
        value: The value to convert.
        encoding: The encoding to use in the conversion.

    Returns:
        The bytes representation of the value.
    """
    if isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        try:
            return value.encode(encoding)
        except UnicodeEncodeError:
            return value.encode("utf-8", "replace")
    else:
        return value


def _to_unicode(value: ICAL_TYPE, encoding="utf-8-sig") -> str:
    """Converts a value to Unicode, even if it is already a Unicode string.

    Parameters:
        value: The value to convert.
        encoding: The encoding to use in the conversion.
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, bytes):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            return value.decode("utf-8-sig", "replace")
    else:
        return value


def _data_encode(
    data: Union[ICAL_TYPE, dict, list], encoding=DEFAULT_ENCODING
) -> Union[bytes, List[bytes], dict]:
    """Encode all datastructures to the given encoding.

    Currently Unicode strings, dicts, and lists are supported.

    Parameters:
        data: The datastructure to encode.
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


__all__ = [
    "DEFAULT_ENCODING",
    "SEQUENCE_TYPES",
    "ICAL_TYPE",
    "_data_encode",
    "_from_unicode",
    "_to_unicode",
]
