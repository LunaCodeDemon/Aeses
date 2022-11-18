"Module for fun commands."
import re
import discord
from discord import app_commands
from discord.ext import commands
from api import pokeapi
from api import safebooru
from configloader import config
from scripts.messagebuilders import generate_booru_message


class Fun(commands.Cog):
    "This cog contains various fun commands"

    def __init__(self, client: commands.Bot):
        "Initialiser for 'Fun' cog."
        self.client = client

    @app_commands.command()
    async def pokemon(self, inter: discord.Interaction, *, name: str = None):
        """
            Searches for a pokemon.
        """

        await inter.response.defer()

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
            await inter.followup.send(config['dialogs']['pokemon']['on_fail']
                                      .format(pokename=name))
            return

        # send the created embed.
        await inter.followup.send(embed=pokemon_embed)

    @app_commands.command()
    async def booru(self, inter: discord.Interaction, *, tags: str):
        """
            Get image from safebooru.org
        """

        await inter.response.defer()

        # pull a random booru post.
        post = await safebooru.random_post(re.split(r"[\s,+]+", tags))

        # build an embed from the booru data
        embed = generate_booru_message(post)

        # respond with the embed.
        await inter.followup.send(embed=embed)


async def setup(client: commands.Bot):
    "Setup function for Fun command collection."
    await client.add_cog(Fun(client))
