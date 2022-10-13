"Module for conversion functions"


def str2bool(val, default: bool = False) -> bool:
    "Converts a string to the correct boolean"

    # return default if val None or empty string.
    if val in [None, ""]:
        return default

    # directly return if val is a boolean.
    if isinstance(val, bool):
        return val

    return val.lower() in ['true', 'yes', 't', '1']


def str2only_ascii(val: str) -> bool:
    "Removes non ascii characters"
    return val.encode("ascii", "ignore").decode()
