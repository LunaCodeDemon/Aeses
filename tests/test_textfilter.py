"Testing functions of textfilter.py"

from scripts.textfilter import check_for_emoji, check_for_links


def test_emoji_check():
    "Test if emoji can be filtered."
    result = check_for_emoji("acdäü❤️-2")
    assert result is True


def test_link_check():
    "Test if links can be detected."
    result = check_for_links("Click here now: https://youtube.com/?w=ohmyfish")
    assert result is True
