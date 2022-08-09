"Tests for safebooru api functions. (May fail if safebooru is down)"
from typing import Optional
import pytest
from api import safebooru

@pytest.mark.asyncio
async def test_random_post():
    "Test for the random post method of the booru command"
    post: Optional[safebooru.SafebooruPost] = await safebooru.random_post()

    assert post is not None or post.post_id > 0
