"Module for testing conversion functions."
from scripts import conversion


def test_str2bool():
    "Testing string 2 boolean conversion"
    assert conversion.str2bool("true")
    assert conversion.str2bool("false") is False

def test_str2only_ascii():
    "Testing string 2 ascii only"
    result = conversion.str2only_ascii("hello❤️")
    assert result == "hello"
