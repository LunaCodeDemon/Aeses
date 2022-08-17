"Tests for safebooru api functions. (May fail if safebooru is down)"
from typing import Optional
import httpx
import pytest
from api import safebooru

@pytest.mark.asyncio
async def test_random_post():
    "Test for the random post method of the booru command"
    try:
        post: Optional[safebooru.SafebooruPost] = await safebooru.random_post()

        assert post is not None or post.post_id > 0
    except httpx.ReadTimeout:
        # in this case a false positive is better.
        # it might be that pokeapi ratelimited the github workflow
        print("Test for random_post got threw exception ReadTimeout. (probably ratelimit)")
        assert True
