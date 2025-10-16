"""Tests for the emotes cog."""
from unittest import mock

import pytest
import hikari

from cogs import emotes as emotes_cog


@pytest.fixture
def mock_emote_config():
    """Fixture for a mocked config dictionary for emotes."""
    config_data = {
        "emotes": {
            "hug": {
                "with_target": "{myself} hugs {target}",
                "alone": "{myself} hugs themselves",
            }
        },
        "emote_links": {"hug": ["http://example.com/hug.gif"]},
    }
    with mock.patch.dict(emotes_cog.config, config_data, clear=True):
        with mock.patch.dict(
            emotes_cog.emote_links, config_data["emote_links"], clear=True
        ):
            yield


def test_generate_emoji_embed(mock_emote_config):
    """Test the emoji embed generation logic."""
    # The mock_emote_config fixture is required to patch the config data
    _ = mock_emote_config

    myself = mock.Mock(spec=hikari.User)
    myself.mention = "@Me"
    target = mock.Mock(spec=hikari.User)
    target.mention = "@Target"

    # Test with target
    embed = emotes_cog.generate_emoji_embed("hug", myself, target)
    assert embed.description == "@Me hugs @Target"
    assert embed.image.url == "http://example.com/hug.gif"

    # Test without target
    embed = emotes_cog.generate_emoji_embed("hug", myself, None)
    assert embed.description == "@Me hugs themselves"
    assert embed.image.url == "http://example.com/hug.gif"


@pytest.mark.anyio
async def test_create_emote_command(mock_ctx, mock_emote_config):
    """Test the command factory to ensure it creates a working command."""
    # The mock_emote_config fixture is required to patch the config data
    _ = mock_emote_config

    # Create a command using the factory
    hug_command = emotes_cog.create_emote_command("hug", "Hug someone.")

    # Test command execution without a target
    await hug_command.callback(mock_ctx, None)
    mock_ctx.respond.assert_called_once()
    call_args = mock_ctx.respond.call_args
    embed = call_args.kwargs["embed"]
    assert embed.description == "@TestAuthor hugs themselves"

    # Test command execution with a target
    mock_ctx.reset_mock()
    target_user = mock.Mock(spec=hikari.User)
    target_user.mention = "@TargetUser"
    await hug_command.callback(mock_ctx, target_user)
    mock_ctx.respond.assert_called_once()
    call_args = mock_ctx.respond.call_args
    embed = call_args.kwargs["embed"]
    assert embed.description == "@TestAuthor hugs @TargetUser"