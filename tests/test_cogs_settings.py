"""Tests for the settings cog."""
from unittest import mock

import pytest

from cogs import settings as settings_cog
from scripts import sqldata


@pytest.mark.anyio
@mock.patch.object(sqldata, "get_filterconfig")
@mock.patch.object(settings_cog, "generate_filtertype_listing", side_effect=str)
async def test_filterconf_list(
    mock_generate_listing, mock_get_config, mock_ctx
):
    """Test the filterconf command when listing filters."""
    _ = mock_generate_listing  # Unused argument
    mock_get_config.return_value = [
        mock.Mock(filter_type=sqldata.FilterType.EMOJI_NAME, active=True),
        mock.Mock(filter_type=sqldata.FilterType.LINK, active=False),
    ]

    await settings_cog.filterconf_command(mock_ctx, filter_type=None, active=None)

    mock_get_config.assert_called_once_with(12345)
    mock_ctx.respond.assert_called_once()

    call_args = mock_ctx.respond.call_args
    embed = call_args.kwargs["embed"]

    assert embed.title == "Filters"
    assert len(embed.fields) == 2
    assert "Active" in embed.fields[0].name
    assert "Inactive" in embed.fields[1].name


@pytest.mark.anyio
@mock.patch.object(sqldata, "get_filterconfig")
@mock.patch.object(sqldata, "insert_filterconfig")
async def test_filterconf_toggle(mock_insert_config, mock_get_config, mock_ctx):
    """Test the filterconf command when toggling a filter."""
    # Test toggling from False to True
    mock_get_config.return_value = [mock.Mock(active=False)]

    await settings_cog.filterconf_command(mock_ctx, filter_type="emona", active=None)

    mock_get_config.assert_called_once_with(12345, sqldata.FilterType.EMOJI_NAME)
    mock_insert_config.assert_called_once_with(
        12345, sqldata.FilterType.EMOJI_NAME, True
    )
    mock_ctx.respond.assert_called_once_with("Filter settings updated.")


@pytest.mark.anyio
@mock.patch.object(sqldata, "insert_filterconfig")
async def test_filterconf_set_static(mock_insert_config, mock_ctx):
    """Test the filterconf command when setting a filter to a static value."""
    await settings_cog.filterconf_command(mock_ctx, filter_type="links", active=True)

    mock_insert_config.assert_called_once_with(12345, sqldata.FilterType.LINK, True)
    mock_ctx.respond.assert_called_once_with("Filter settings updated.")
