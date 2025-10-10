import pytest
import unittest.mock as mock
import hikari
import tanjun
import ongaku
from cogs import music as music_cog

@pytest.mark.anyio
async def test_play_command_no_voice_state(mock_ctx):
    """Test the play command when the user is not in a voice channel."""
    mock_ctx.member.voice_state = None

    await music_cog.play_command(mock_ctx, "some query")

    mock_ctx.respond.assert_called_once_with("You must be in a voice channel to use this command.")

@pytest.mark.anyio
async def test_disconnect_command(mock_ctx):
    """Test the disconnect command."""
    mock_ongaku = mock.AsyncMock(spec=ongaku.Client)
    mock_ongaku.disconnect = mock.AsyncMock()

    await music_cog.disconnect_command(mock_ctx, ongaku_client=mock_ongaku)

    mock_ongaku.disconnect.assert_called_once_with(mock_ctx.guild_id)
    mock_ctx.respond.assert_called_once_with("Disconnected from the channel.")

@pytest.mark.anyio
async def test_volume_command(mock_ctx):
    """Test the volume command."""
    mock_ongaku = mock.AsyncMock(spec=ongaku.Client)
    mock_player = mock.AsyncMock(spec=ongaku.Player)
    mock_ongaku.fetch_player.return_value = mock_player

    await music_cog.volume_command(mock_ctx, percentage=50, ongaku_client=mock_ongaku)

    mock_ongaku.fetch_player.assert_called_once_with(mock_ctx.guild_id)
    mock_player.set_volume.assert_called_once_with(50)
    mock_ctx.respond.assert_called_once_with("Set stream volume to 50%")

@pytest.mark.anyio
@mock.patch("cogs.music.radio_browser.search_radio", return_value=[])
async def test_play_command_radio_search_no_results(mock_search, mock_ctx):
    """Test the play command with a radio search that returns no results."""
    mock_ongaku = mock.AsyncMock(spec=ongaku.Client)
    mock_player = mock.AsyncMock(spec=ongaku.Player)
    mock_player.is_connected = False
    mock_ongaku.create_player = mock.AsyncMock(return_value=mock_player)

    await music_cog.play_command(mock_ctx, "nonexistent radio", ongaku_client=mock_ongaku)

    mock_ctx.defer.assert_called_once()
    mock_ctx.respond.assert_called_once_with("Couldn't find any station matching your search term.")