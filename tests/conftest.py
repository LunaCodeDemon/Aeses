import pytest
import unittest.mock as mock
import tanjun
import hikari

@pytest.fixture
def mock_ctx():
    """Provides a comprehensive mock of a Tanjun context."""
    # We use a real class that inherits from the mock to allow for attributes
    # to be set on it.
    class MockContext(mock.AsyncMock):
        author = mock.Mock(spec=hikari.User)
        member = mock.AsyncMock(spec=hikari.Member)
        guild_id = 12345

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.author.mention = "@TestAuthor"
            self.author.username = "TestAuthor"
            self.author.accent_color = 0x00ffff
            self.author.avatar_url = "http://example.com/author_avatar.png"

            # Make the mock awaitable
            self.__await__ = lambda: self.__async_return_value__.__await__()

    ctx = MockContext(spec=tanjun.abc.Context)

    # Configure the async methods
    ctx.defer = mock.AsyncMock()
    ctx.respond = mock.AsyncMock()
    ctx.create_followup = mock.AsyncMock()
    ctx.edit_initial_response = mock.AsyncMock()
    ctx.fetch_channel = mock.AsyncMock()

    return ctx