"""
test for message builders.
those can only be made if the message builder creates a string.
"""
from scripts.messagebuilders import generate_filtertype_listing
from scripts.sqldata import FilterType


def test_generate_filtertype_listing():
    "Testing filtertype list generator."
    assert generate_filtertype_listing([]) == "none"
    assert generate_filtertype_listing(
        [FilterType.EMOJI_NAME, FilterType.LINK]) == "- emona\n- links"
