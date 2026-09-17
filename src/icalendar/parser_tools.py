SEQUENCE_TYPES = (list, tuple)
DEFAULT_ENCODING = "utf-8"
ICAL_TYPE = str | bytes
INVALID_ENCODING_MESSAGE = (
    "Calendar data is not valid UTF-8. RFC 5545 requires UTF-8. "
    "Pass encoding=... if you know the source encoding, or use "
    "errors='replace' to restore the previous replacement behavior. "
    "See https://github.com/collective/icalendar/issues/1793 and open a "
    "related issue if you need broader encoding support."
)


def from_unicode(value: ICAL_TYPE, encoding: str = "utf-8") -> bytes:
    """Converts a value to bytes, even if it is already bytes.

    Parameters:
        value: The value to convert.
        encoding: The encoding to use in the conversion.

    Returns:
        The bytes representation of the value.
    """
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        try:
            return value.encode(encoding)
        except UnicodeEncodeError:
            return value.encode("utf-8", "replace")
    else:
        return value


def to_unicode(
    value: ICAL_TYPE, encoding: str = "utf-8-sig", errors: str = "strict"
) -> str:
    """Converts a value to Unicode, even if it is already a Unicode string.

    Parameters:
        value: The value to convert.
        encoding: The encoding to use in the conversion.
        errors: The error handling scheme to use when decoding bytes.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        if errors != "strict":
            return value.decode(encoding, errors)
        try:
            return value.decode(encoding, errors)
        except UnicodeDecodeError as error:
            from icalendar.error import InvalidCalendar

            raise InvalidCalendar(INVALID_ENCODING_MESSAGE) from error
    else:
        return value


def data_encode(
    data: ICAL_TYPE | dict | list, encoding: str = DEFAULT_ENCODING
) -> bytes | list[bytes] | dict:
    """Encode all datastructures to the given encoding.

    Currently Unicode strings, dicts, and lists are supported.

    Parameters:
        data: The datastructure to encode.
    """
    # https://stackoverflow.com/questions/1254454/fastest-way-to-convert-a-dicts-keys-values-from-unicode-to-str
    if isinstance(data, str):
        return data.encode(encoding)
    if isinstance(data, dict):
        return dict(map(data_encode, iter(data.items())))
    if isinstance(data, (list, tuple)):
        return list(map(data_encode, data))
    return data


__all__ = [
    "DEFAULT_ENCODING",
    "ICAL_TYPE",
    "SEQUENCE_TYPES",
    "data_encode",
    "from_unicode",
    "to_unicode",
]
