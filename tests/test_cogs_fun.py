import pytest
import unittest.mock as mock
import hikari
import tanjun
from cogs import fun as fun_cog
from api import pokeapi, safebooru

@pytest.mark.anyio
@mock.patch.object(pokeapi, "get_pokemon")
async def test_pokemon_command_with_name(mock_get_pokemon, mock_ctx):
    """Test the pokemon command with a specific pokemon name."""
    # Setup mock data
    mock_pokemon_data = {
        "name": "pikachu",
        "id": 25,
        "sprites": {"front_default": "http://example.com/pikachu.png"},
        "types": [{"type": {"name": "electric"}}],
        "stats": [{"stat": {"name": "hp"}, "base_stat": 35}]
    }
    mock_get_pokemon.return_value = mock_pokemon_data

    # Call the command
    await fun_cog.pokemon_command(mock_ctx, "pikachu")

    # Assertions
    mock_get_pokemon.assert_called_once_with("pikachu")
    mock_ctx.defer.assert_called_once()
    mock_ctx.create_followup.assert_called_once()

    call_args = mock_ctx.create_followup.call_args
    embed = call_args.kwargs['embed']

    assert embed.title == "Pikachu"
    assert embed.description == "ID: 25"
    assert embed.thumbnail.url == "http://example.com/pikachu.png"
    assert len(embed.fields) == 2 # types and one stat

@pytest.mark.anyio
@mock.patch.object(pokeapi, "get_pokemon", return_value=None)
async def test_pokemon_command_fails(mock_get_pokemon, mock_ctx):
    """Test the pokemon command when the API fails to find a pokemon."""
    with mock.patch.dict(fun_cog.config, {"dialogs": {"pokemon": {"on_fail": "Failed to find {pokename}"}}}):
        await fun_cog.pokemon_command(mock_ctx, "notarealpokemon")

        mock_ctx.defer.assert_called_once()
        mock_ctx.create_followup.assert_called_once_with("Failed to find notarealpokemon")

@pytest.mark.anyio
@mock.patch.object(safebooru, "random_post")
async def test_booru_command(mock_random_post, mock_ctx):
    """Test the booru command."""
    mock_post = mock.Mock()
    mock_post.post_id = 123
    mock_post.post_url = "http://example.com/post/123"
    mock_post.has_comments = True
    mock_post.file_url = "http://example.com/image.jpg"
    mock_random_post.return_value = mock_post

    await fun_cog.booru_command(mock_ctx, "some tags")

    mock_ctx.defer.assert_called_once()
    mock_ctx.create_followup.assert_called_once()

    call_args = mock_ctx.create_followup.call_args
    embed = call_args.kwargs['embed']

    assert embed.title == "Post: 123"
    assert embed.image.url == "http://example.com/image.jpg"
    assert "has comments" in embed.footer.text