"""Tests for the utility cog."""
from unittest import mock

import pytest
import hikari
import tanjun

from cogs import utility


@pytest.mark.anyio
async def test_info_command(mock_ctx):
    """Test the info command to ensure it generates a correct embed."""
    bot = mock.AsyncMock(spec=hikari.GatewayBot)

    mock_user = mock.Mock(spec=hikari.User)
    mock_user.username = "TestBot"
    mock_user.avatar_url = "http://example.com/avatar.png"
    bot.get_me.return_value = mock_user

    await utility.info_command(mock_ctx, bot=bot)

    mock_ctx.respond.assert_called_once()
    call_args = mock_ctx.respond.call_args
    embed = call_args.kwargs["embed"]

    assert embed.title == "TestBot"
    assert embed.image.url == "http://example.com/avatar.png"


@pytest.mark.anyio
async def test_invite_command(mock_ctx):
    """Test the invite command to ensure it generates a correct invite link."""
    bot = mock.AsyncMock(spec=hikari.GatewayBot)

    mock_app = mock.Mock(spec=hikari.Application)
    mock_app.id = 1234567890
    bot.application = mock_app

    await utility.invite_command(mock_ctx, bot=bot)

    mock_ctx.respond.assert_called_once()
    call_args = mock_ctx.respond.call_args
    embed = call_args.kwargs["embed"]

    assert "Invite" in embed.title
    assert (
        "https://discord.com/api/oauth2/authorize?client_id=1234567890"
        in embed.description
    )


@pytest.mark.anyio
async def test_avatar_command(mock_ctx):
    """Test the avatar command for both specified user and default author."""
    user = mock.Mock(spec=hikari.User)
    user.username = "TestUser"
    user.accent_color = 0xFF00FF
    user.avatar_url = "http://example.com/user_avatar.png"

    await utility.avatar_command(mock_ctx, user)

    mock_ctx.respond.assert_called_once()
    call_args = mock_ctx.respond.call_args
    embed = call_args.kwargs["embed"]

    assert embed.title == "TestUser"
    assert embed.image.url == "http://example.com/user_avatar.png"


@pytest.mark.anyio
async def test_whois_command(mock_ctx):
    """Test the whois slash command."""
    member = mock.AsyncMock(spec=hikari.Member)
    member.display_name = "TestMember"
    member.accent_color = 0x00FF00
    member.display_avatar_url = "http://example.com/member_avatar.png"
    member.get_roles.return_value = []
    member.created_at.strftime.return_value = "01/01/2023, 12:00:00"
    member.joined_at.strftime.return_value = "01/01/2024, 12:00:00"

    await utility.whois_command(mock_ctx, member)

    mock_ctx.respond.assert_called_once()
    call_args = mock_ctx.respond.call_args
    embed = call_args.kwargs["embed"]

    assert "Whois of TestMember" in embed.title
    assert embed.thumbnail.url == "http://example.com/member_avatar.png"


@pytest.mark.anyio
async def test_whois_menu_command():
    """Test the whois context menu command."""
    ctx = mock.AsyncMock(spec=tanjun.abc.MenuContext)
    member = mock.AsyncMock(spec=hikari.Member)
    member.display_name = "MenuMember"
    member.accent_color = 0xFF0000
    member.display_avatar_url = "http://example.com/menu_avatar.png"
    member.get_roles.return_value = []
    member.created_at.strftime.return_value = "02/02/2023, 12:00:00"
    member.joined_at.strftime.return_value = "02/02/2024, 12:00:00"

    await utility.whois_menu(ctx, member)

    ctx.respond.assert_called_once()
    call_args = ctx.respond.call_args
    embed = call_args.kwargs["embed"]

    assert "Whois of MenuMember" in embed.title
    assert embed.thumbnail.url == "http://example.com/menu_avatar.png"


@pytest.mark.anyio
async def test_avatar_menu_command():
    """Test the avatar context menu command."""
    ctx = mock.AsyncMock(spec=tanjun.abc.MenuContext)
    user = mock.Mock(spec=hikari.User)
    user.username = "MenuUser"
    user.accent_color = 0x0000FF
    user.avatar_url = "http://example.com/menu_user_avatar.png"

    await utility.avatar_menu(ctx, user)

    ctx.respond.assert_called_once()
    call_args = ctx.respond.call_args
    embed = call_args.kwargs["embed"]

    assert embed.title == "MenuUser"
    assert embed.image.url == "http://example.com/menu_user_avatar.png"
