"A command group containing emote commands."
from random import choice
import functools
import discord
from discord.ext import commands
from configloader import config, emote_links


def emoji_command(func):
    "Emoji command decoration."
    @functools.wraps(func)
    async def decorator(self, ctx, target: discord.Member = None):
        embed = discord.Embed()
        if target:
            embed.description = (
                config['emotes'][func.__name__]['with_target']
                .format(myself=ctx.author.mention, target=target.mention)
            )
        else:
            embed.description = (
                config['emotes'][func.__name__]['alone']
                .format(myself=ctx.author.mention)
            )
        embed.set_image(url=choice(emote_links[func.__name__]))
        await ctx.send(embed=embed)
        func(self, ctx, target)
    return decorator


class Emotes(commands.Cog):
    "A command group containing emote commands."

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command()
    @emoji_command
    def hug(self, ctx, target: discord.Member = None):
        "Hug someone."

    @commands.command()
    @emoji_command
    def cry(self, ctx, target: discord.Member = None):
        "For the sad times."

    @commands.command()
    @emoji_command
    def smile(self, ctx, target: discord.Member = None):
        "For happy times."

    @commands.command()
    @emoji_command
    def smug(self, ctx, target: discord.Member = None):
        "surely something weird is happening."

    @commands.command()
    @emoji_command
    def pat(self, ctx, target: discord.Member = None):
        "Nice pats."


async def setup(client: commands.Bot):
    "setup function of this cog."
    await client.add_cog(Emotes(client))
