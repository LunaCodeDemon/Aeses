"""Global fixtures for Pytest."""
from unittest import mock

import pytest
import hikari
import tanjun


@pytest.fixture
def mock_ctx() -> mock.AsyncMock:
    """Provides a comprehensive mock of a Tanjun context."""
    ctx = mock.AsyncMock(spec=tanjun.abc.Context)
    ctx.author = mock.Mock(spec=hikari.User)
    ctx.member = mock.AsyncMock(spec=hikari.Member)
    ctx.guild_id = 12345

    ctx.author.mention = "@TestAuthor"
    ctx.author.username = "TestAuthor"
    ctx.author.accent_color = 0x00FFFF
    ctx.author.avatar_url = "http://example.com/author_avatar.png"

    ctx.member.voice_state = mock.Mock(spec=hikari.VoiceState)
    ctx.member.voice_state.channel_id = 987654321

    # Re-adding the essential async methods to the mock
    ctx.defer = mock.AsyncMock()
    ctx.respond = mock.AsyncMock()
    ctx.create_followup = mock.AsyncMock()
    ctx.edit_initial_response = mock.AsyncMock()
    ctx.fetch_channel = mock.AsyncMock()

    return ctx