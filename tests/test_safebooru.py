"Tests for safebooru api functions."
from unittest import mock

import pytest

from api import safebooru

# Sample XML responses for mocking
MOCK_COUNT_XML = '<posts count="10" offset="0"></posts>'
MOCK_POST_XML = """
<posts count="1" offset="0">
    <post
        height="1200"
        score="5"
        file_url="//g.safebooru.org/images/1/1a2b3c.jpg"
        parent_id=""
        sample_url="//g.safebooru.org/samples/1/sample_1a2b3c.jpg"
        sample_width="850"
        sample_height="600"
        preview_url="//g.safebooru.org/thumbnails/1/thumbnail_1a2b3c.jpg"
        rating="safe"
        tags="tag1 tag2"
        id="12345"
        width="1700"
        change="1609459200"
        md5="abcdef123456"
        creator_id="9876"
        has_children="false"
        created_at="Sat Jan 01 00:00:00 +0100 2021"
        status="active"
        source="some_source"
        has_notes="false"
        has_comments="true"
    />
</posts>
"""


@pytest.mark.anyio
@mock.patch("api.safebooru.httpx.get")
async def test_random_post_mocked(mock_get):
    """Test for the random post method of the booru command with a mocked API."""
    # Configure the mock response
    # The count call returns the count, the post call returns the post data
    mock_get.side_effect = [
        mock.Mock(status_code=200, text=MOCK_COUNT_XML),
        mock.Mock(status_code=200, text=MOCK_POST_XML),
    ]

    # Call the function
    post = await safebooru.random_post()

    # Assertions
    assert post is not None
    assert post.post_id == 12345
    assert post.file_url == "//g.safebooru.org/images/1/1a2b3c.jpg"
    assert post.has_comments is True
    assert "tag1" in post.tags


@pytest.mark.anyio
@mock.patch("api.safebooru.httpx.get")
async def test_random_post_no_results(mock_get):
    """Test the random_post function when the API returns no results."""
    mock_count_response = mock.Mock()
    mock_count_response.status_code = 200
    mock_count_response.text = '<posts count="0" offset="0"></posts>'
    mock_get.return_value = mock_count_response

    with pytest.raises(safebooru.SafebooruNothingFound):
        await safebooru.random_post()
