"Module for conversion functions"


def str2bool(val, default: bool = False) -> bool:
    "Converts a string to the correct boolean"
    if not val:
        return default
    if isinstance(val, bool):
        return val
    return val.lower() in ['true', 'yes', 't', '1']


def str2only_ascii(val: str) -> bool:
    "Removes non ascii characters"
    return val.encode("ascii", "ignore").decode()
