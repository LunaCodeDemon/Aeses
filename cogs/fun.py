"Module for fun commands."
import re
import hikari
import tanjun
from api import pokeapi, safebooru
from configloader import config

component = tanjun.Component()


@component.with_slash_command
@tanjun.with_str_slash_option(
    "name", "The name of the Pokémon to search for.", default=None
)
@tanjun.as_slash_command("pokemon", "Searches for a Pokémon.")
async def pokemon_command(ctx: tanjun.abc.Context, name: str | None):
    """Searches for a pokemon."""
    await ctx.defer()

    pokemon_data = (
        pokeapi.get_random_pokemon() if not name else pokeapi.get_pokemon(name.lower())
    )

    embed = pokeapi.create_pokemon_embed(pokemon_data)

    if not embed:
        fail_message = (
            config["dialogs"]["pokemon"]["on_fail"].format(pokename=name)
            if name
            else "Could not find a random Pokémon."
        )
        await ctx.create_followup(fail_message)
        return

    await ctx.create_followup(embed=embed)


@component.with_slash_command
@tanjun.with_str_slash_option("tags", "Tags to search for, separated by spaces.")
@tanjun.as_slash_command("booru", "Get an image from safebooru.org")
async def booru_command(ctx: tanjun.abc.Context, tags: str):
    """Get image from safebooru.org"""
    await ctx.defer()

    post = await safebooru.random_post(re.split(r"[\s,+]+", tags))

    if not post or not hasattr(post, "file_url"):
        await ctx.create_followup("Could not find an image with those tags.")
        return

    embed = hikari.Embed()
    embed.title = f"Post: {post.post_id}"
    embed.description = f"You can find the post here: {post.post_url}"
    embed.set_footer(
        text="Post has comments" if post.has_comments else "Post has no comments."
    )
    embed.set_image(post.file_url)

    await ctx.create_followup(embed=embed)


@tanjun.as_loader
def load_component(client: tanjun.Client):
    "Loads the component"
    client.add_component(component.copy())
