"""Tests for the moderation cog."""
from unittest import mock

import pytest
import hikari

from cogs import moderation as moderation_cog


@pytest.mark.anyio
async def test_nsfw_command(mock_ctx):
    """Test the nsfw command logic."""
    mock_channel = mock.AsyncMock(spec=hikari.GuildTextChannel)
    mock_ctx.fetch_channel.return_value = mock_channel

    # Test toggling NSFW from False to True
    mock_channel.is_nsfw = False
    with mock.patch.dict(
        moderation_cog.config,
        {"dialogs": {"nsfw": {"response": "Channel {channel} is now {status}"}}},
    ):
        await moderation_cog.nsfw_command(mock_ctx, static_value=None)
        mock_channel.edit.assert_called_once_with(nsfw=True)

    # Test toggling NSFW from True to False
    mock_channel.reset_mock()
    mock_channel.is_nsfw = True
    with mock.patch.dict(
        moderation_cog.config,
        {"dialogs": {"nsfw": {"response": "Channel {channel} is now {status}"}}},
    ):
        await moderation_cog.nsfw_command(mock_ctx, static_value=None)
        mock_channel.edit.assert_called_once_with(nsfw=False)

    # Test setting NSFW to a static value (True)
    mock_channel.reset_mock()
    with mock.patch.dict(
        moderation_cog.config,
        {"dialogs": {"nsfw": {"response": "Channel {channel} is now {status}"}}},
    ):
        await moderation_cog.nsfw_command(mock_ctx, static_value=True)
        mock_channel.edit.assert_called_once_with(nsfw=True)

    # Test setting NSFW to a static value (False)
    mock_channel.reset_mock()
    with mock.patch.dict(
        moderation_cog.config,
        {"dialogs": {"nsfw": {"response": "Channel {channel} is now {status}"}}},
    ):
        await moderation_cog.nsfw_command(mock_ctx, static_value=False)
        mock_channel.edit.assert_called_once_with(nsfw=False)


@pytest.mark.anyio
async def test_slowdown_command(mock_ctx):
    """Test the slowdown command logic."""
    mock_channel = mock.AsyncMock(spec=hikari.GuildTextChannel)
    mock_ctx.fetch_channel.return_value = mock_channel

    # Test setting a slowdown
    await moderation_cog.slowdown_command(mock_ctx, seconds=10)
    mock_channel.edit.assert_called_once_with(slow_mode_cooldown=10)
    mock_ctx.respond.assert_called_once_with("Successfully changed slowmode settings.")

    # Test disabling the slowdown
    mock_channel.reset_mock()
    mock_ctx.respond.reset_mock()
    await moderation_cog.slowdown_command(mock_ctx, seconds=0)
    mock_channel.edit.assert_called_once_with(slow_mode_cooldown=0)
