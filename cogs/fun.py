"Module for fun commands."
from typing import List, Tuple
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

    @commands.command()
    async def pokemon(self, ctx: commands.Context, *, name: str = None):
        "Searches for a pokemon."
        # grab data from pokeapi
        pokemon_data: any
        if name:
            pokemon_data = pokeapi.get_pokemon(name.lower())
        else:
            pokemon_data = pokeapi.get_random_pokemon()
        # turn data into embed
        pokemon_embed = pokeapi.gen_pokemon_embed(pokemon_data)
        if not pokemon_embed:
            await ctx.send(config['dialogs']['pokemon']['on_fail']
                           .format(pokename=name))
            return
        await ctx.send(embed=pokemon_embed)

    @commands.command()
    async def booru(self, ctx: commands.Context, *tags: str):
        "Get image from safebooru.org"
        post = await safebooru.random_post(tags)

        embed = Embed()
        embed.title = f"Post: {post.post_id}"
        embed.description = f"You will find the post here: {post.post_url}"
        embed.set_footer(
            text="Post has comments" if post.has_comments else "Post has no comments.")
        embed.set_image(url=post.file_url)
        await ctx.send(embed=embed)


async def setup(client: commands.Bot):
    "Setup function for Fun command collection."
    await client.add_cog(Fun(client))
