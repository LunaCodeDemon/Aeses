"Module for fun commands."
import re
import hikari
import tanjun
from api import pokeapi, safebooru
from configloader import config

component = tanjun.Component()

def create_pokemon_embed(pokemon_data: dict) -> hikari.Embed:
    """Generates an embed from Pokémon data."""
    if not pokemon_data:
        return None

    name = pokemon_data.get('name', 'Unknown').capitalize()
    poke_id = pokemon_data.get('id', 'N/A')

    embed = hikari.Embed(
        title=name,
        description=f"ID: {poke_id}"
    )

    if sprites := pokemon_data.get('sprites'):
        if front_default := sprites.get('front_default'):
            embed.set_thumbnail(front_default)

    if types_data := pokemon_data.get('types'):
        types = ", ".join([t['type']['name'] for t in types_data])
        embed.add_field("Types", types, inline=True)

    if stats_data := pokemon_data.get('stats'):
        for stat in stats_data:
            stat_name = stat['stat']['name'].replace('-', ' ').capitalize()
            embed.add_field(stat_name, str(stat['base_stat']), inline=True)

    return embed

@component.with_slash_command
@tanjun.with_str_slash_option("name", "The name of the Pokémon to search for.", default=None)
@tanjun.as_slash_command("pokemon", "Searches for a Pokémon.")
async def pokemon_command(ctx: tanjun.abc.Context, name: str | None):
    """Searches for a pokemon."""
    await ctx.defer()

    pokemon_data = pokeapi.get_random_pokemon() if not name else pokeapi.get_pokemon(name.lower())

    embed = create_pokemon_embed(pokemon_data)

    if not embed:
        await ctx.create_followup(config['dialogs']['pokemon']['on_fail'].format(pokename=name or "a random pokemon"))
        return

    await ctx.create_followup(embed=embed)

@component.with_slash_command
@tanjun.with_str_slash_option("tags", "Tags to search for, separated by spaces.")
@tanjun.as_slash_command("booru", "Get an image from safebooru.org")
async def booru_command(ctx: tanjun.abc.Context, tags: str):
    """Get image from safebooru.org"""
    await ctx.defer()

    post = await safebooru.random_post(re.split(r"[\s,+]+", tags))

    if not post or not hasattr(post, 'file_url'):
        await ctx.create_followup("Could not find an image with those tags.")
        return

    embed = hikari.Embed()
    embed.title = f"Post: {post.post_id}"
    embed.description = f"You can find the post here: {post.post_url}"
    embed.set_footer(text="Post has comments" if post.has_comments else "Post has no comments.")
    embed.set_image(url=post.file_url)

    await ctx.create_followup(embed=embed)

@tanjun.as_loader
def load_component(client: tanjun.Client):
    "Loads the component"
    client.add_component(component.copy())