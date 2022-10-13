"Module for fun commands."
import re
from discord import Embed
from discord.ext import commands
from api import pokeapi
from api import safebooru
from configloader import config


class Fun(commands.Cog):
    "This cog contains various fun commands"

    def __init__(self, client: commands.Bot):
        "Initialiser for 'Fun' cog."
        self.client = client

    @commands.hybrid_command()
    async def pokemon(self, ctx: commands.Context, *, name: str = None):
        "Searches for a pokemon."
        # grab data from pokeapi, depending on what name was given (or not)
        pokemon_data: any
        if name:
            pokemon_data = pokeapi.get_pokemon(name.lower())
        else:
            pokemon_data = pokeapi.get_random_pokemon()

        # turn data into embed
        pokemon_embed = pokeapi.gen_pokemon_embed(pokemon_data)

        # send a on_fail response if the embed wasn't created.
        if not pokemon_embed:
            await ctx.send(config['dialogs']['pokemon']['on_fail']
                           .format(pokename=name))
            return

        # send the created embed.
        await ctx.send(embed=pokemon_embed)

    @commands.hybrid_command()
    async def booru(self, ctx: commands.Context, *, tags: str):
        "Get image from safebooru.org"
        # pull a random booru post.
        post = await safebooru.random_post(re.split(r"[\s,+]+", tags))

        # build an embed from the booru data
        embed = Embed()
        embed.title = f"Post: {post.post_id}"
        embed.description = f"You will find the post here: {post.post_url}"
        embed.set_footer(
            text="Post has comments" if post.has_comments else "Post has no comments.")
        embed.set_image(url=post.file_url)

        # respond with the embed.
        await ctx.send(embed=embed)


async def setup(client: commands.Bot):
    "Setup function for Fun command collection."
    await client.add_cog(Fun(client))
