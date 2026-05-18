import warnings

SEQUENCE_TYPES = (list, tuple)
DEFAULT_ENCODING = "utf-8"
ICAL_TYPE = str | bytes


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
    if isinstance(value, str):
        try:
            return value.encode(encoding)
        except UnicodeEncodeError:
            return value.encode("utf-8", "replace")
    else:
        return value


def from_unicode(value: ICAL_TYPE, encoding="utf-8") -> bytes:
    """Converts a value to bytes, even if it is already bytes.

    .. deprecated:: 7.0.0
        Use the private :func:`_from_unicode` internally. For external use,
        this function is deprecated. Please contact the maintainers if you
        rely on this function.
    """
    warnings.warn(
        "from_unicode is deprecated and will be removed in a future version. "
        "If you are using this function externally, please contact the maintainers.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _from_unicode(value, encoding)


def _to_unicode(value: ICAL_TYPE, encoding="utf-8-sig") -> str:
    """Converts a value to Unicode, even if it is already a Unicode string.

    Parameters:
        value: The value to convert.
        encoding: The encoding to use in the conversion.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            return value.decode("utf-8-sig", "replace")
    else:
        return value


def to_unicode(value: ICAL_TYPE, encoding="utf-8-sig") -> str:
    """Converts a value to Unicode, even if it is already a Unicode string.

    .. deprecated:: 7.0.0
        Use the private :func:`_to_unicode` internally. For external use,
        this function is deprecated. Please contact the maintainers if you
        rely on this function.
    """
    warnings.warn(
        "to_unicode is deprecated and will be removed in a future version. "
        "If you are using this function externally, please contact the maintainers.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _to_unicode(value, encoding)


def _data_encode(
    data: ICAL_TYPE | dict | list, encoding=DEFAULT_ENCODING
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
        return dict(map(_data_encode, iter(data.items())))
    if isinstance(data, (list, tuple)):
        return list(map(_data_encode, data))
    return data


def data_encode(
    data: ICAL_TYPE | dict | list, encoding=DEFAULT_ENCODING
) -> bytes | list[bytes] | dict:
    """Encode all datastructures to the given encoding.

    .. deprecated:: 7.0.0
        Use the private :func:`_data_encode` internally. For external use,
        this function is deprecated. Please contact the maintainers if you
        rely on this function.
    """
    warnings.warn(
        "data_encode is deprecated and will be removed in a future version. "
        "If you are using this function externally, please contact the maintainers.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _data_encode(data, encoding)


__all__ = [
    "DEFAULT_ENCODING",
    "ICAL_TYPE",
    "SEQUENCE_TYPES",
    "_data_encode",
    "_from_unicode",
    "_to_unicode",
    "data_encode",
    "from_unicode",
    "to_unicode",
]
