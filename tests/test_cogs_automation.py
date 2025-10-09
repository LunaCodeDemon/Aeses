import pytest
import unittest.mock as mock
import hikari
import tanjun
from cogs import automation as automation_cog
from scripts import sqldata

@pytest.mark.anyio
@mock.patch("cogs.automation.sqldata.insert_reminder")
async def test_reminder_command(mock_insert_reminder, mock_ctx):
    """Test the reminder command."""
    await automation_cog.reminder_command(mock_ctx, note="Test reminder", seconds=60)

    # Verify that the command tried to create a reminder in the database
    mock_insert_reminder.assert_called_once()

    # Check that it responded to the user
    mock_ctx.defer.assert_called_once()
    mock_ctx.create_followup.assert_called_once()

    # Check the content of the response
    call_args = mock_ctx.create_followup.call_args
    assert "Reminder scheduled for" in call_args.args[0]

@pytest.mark.anyio
@mock.patch("cogs.automation.sqldata.insert_logchannel")
async def test_log_add_command(mock_insert_logchannel, mock_ctx):
    """Test the log add command."""
    mock_channel = mock.AsyncMock(spec=hikari.InteractionChannel)
    mock_channel.id = 98765

    await automation_cog.log_add_command(
        mock_ctx,
        logtype=sqldata.LogType.WELCOME.value,
        channel=mock_channel
    )

    # Verify that the database function was called correctly
    mock_insert_logchannel.assert_called_once_with(
        mock_ctx.guild_id,
        mock_channel.id,
        sqldata.LogType.WELCOME
    )

    # Check that it responded to the user
    mock_ctx.respond.assert_called_once()
    assert "Activated" in mock_ctx.respond.call_args.args[0]

@pytest.mark.anyio
@mock.patch("cogs.automation.sqldata.get_logchannel")
async def test_log_list_command(mock_get_logchannel, mock_ctx):
    """Test the log list command."""
    # Mock the database response
    mock_get_logchannel.return_value = [
        mock.Mock(logtype=sqldata.LogType.WELCOME, channel_id=111),
        mock.Mock(logtype=sqldata.LogType.MODERATION, channel_id=222)
    ]

    await automation_cog.log_list_command(mock_ctx)

    # Verify that the database function was called
    mock_get_logchannel.assert_called_once_with(mock_ctx.guild_id)

    # Check that an embed was sent
    mock_ctx.respond.assert_called_once()
    call_args = mock_ctx.respond.call_args
    embed = call_args.kwargs['embed']

    assert embed.title == "Active log channels."
    assert len(embed.fields) == 2
    assert embed.fields[0].name == "WELCOME"
    assert embed.fields[0].value == "<#111>"

@pytest.mark.anyio
@mock.patch("cogs.automation.sqldata.get_logchannel", return_value=[])
async def test_log_list_command_empty(mock_get_logchannel, mock_ctx):
    """Test the log list command when no channels are configured."""
    await automation_cog.log_list_command(mock_ctx)

    mock_get_logchannel.assert_called_once_with(mock_ctx.guild_id)
    mock_ctx.respond.assert_called_once_with("No log channels selected.")