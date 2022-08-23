SEQUENCE_TYPES = (list, tuple)
DEFAULT_ENCODING = 'utf-8'


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
