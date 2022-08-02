"Module for fun commands."
from discord.ext import commands
from scripts import pokeapi

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
            pokemon_data = pokeapi.get_pokemon(name)
        else:
            pokemon_data = pokeapi.get_random_pokemon()
        # turn data into embed
        pokemon_embed = pokeapi.gen_pokemon_embed(pokemon_data)
        if not pokemon_embed:
            await ctx.send(config['dialog_pokemon']['on_fail']
                .format(pokename=name))
            return
        await ctx.send(embed=pokemon_embed)

def setup(client: commands.Bot):
    "Setup function for Fun command collection."
    client.add_cog(Fun(client))
