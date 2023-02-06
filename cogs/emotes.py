"A command group containing emote commands."
from random import choice
import functools
import discord
from discord import app_commands
from discord.ext import commands
from configloader import config, emote_links
from bot import AesesBot


def generate_emoji_embed(action: str, myself: str, target: str = None):
    "Generates an emoji for an emote"
    embed = discord.Embed()
    if target:
        embed.description = (config['emotes'][action]['with_target'].format(
            myself=myself, target=target))

    else:
        embed.description = (config['emotes'][action]['alone'].format(
            myself=myself))

    embed.color = discord.Color(0xff3300)

    embed.set_image(url=choice(emote_links[action]))

    return embed


def emoji_command(func):
    "Emoji command decoration."

    @functools.wraps(func)
    async def decorator(self,
                        inter: discord.Interaction,
                        target: discord.Member = None):
        embed = generate_emoji_embed(func.__name__, inter.user.mention,
                                     target.mention if target else None)
        await inter.response.send_message(embed=embed)
        func(self, inter, target)

    return decorator


class Emotes(commands.Cog):
    """
        A command group containing emote commands.
        Those will have a descriptive text, for each action.
        The text will be selected depending if someone was mentioned/selected per argument.
    """
    def __init__(self, client: AesesBot) -> None:
        self.client = client

    # repeating app emote commands that are using the @emoji_command decorator.

    @app_commands.command()
    @emoji_command
    def hug(self, inter: discord.Interaction, target: discord.Member = None):
        "Hug someone."

    @app_commands.command()
    @emoji_command
    def cry(self, inter: discord.Interaction, target: discord.Member = None):
        "For the sad times."

    @app_commands.command()
    @emoji_command
    def smile(self, inter: discord.Interaction, target: discord.Member = None):
        "For happy times."

    @app_commands.command()
    @emoji_command
    def smug(self, inter: discord.Interaction, target: discord.Member = None):
        "surely something weird is happening."

    @app_commands.command()
    @emoji_command
    def pat(self, inter: discord.Interaction, target: discord.Member = None):
        "Nice pats."

    @app_commands.command()
    @emoji_command
    def blush(self, inter: discord.Interaction, target: discord.Member = None):
        "Do a blush"

    @app_commands.command()
    @emoji_command
    def boop(self, inter: discord.Interaction, target: discord.Member = None):
        "Boop someone"

    @app_commands.command()
    @emoji_command
    def highfive(self,
                 inter: discord.Interaction,
                 target: discord.Member = None):
        "Highfive someone"

    @app_commands.command()
    @emoji_command
    def kiss(self, inter: discord.Interaction, target: discord.Member = None):
        "Kiss someone"

    @app_commands.command()
    @emoji_command
    def nom(self, inter: discord.Interaction, target: discord.Member = None):
        "Nom someone"

    @app_commands.command()
    @emoji_command
    def stare(self, inter: discord.Interaction, target: discord.Member = None):
        "Stareing..."

    @app_commands.command()
    @emoji_command
    def wave(self, inter: discord.Interaction, target: discord.Member = None):
        "Waving.."

    @app_commands.command()
    @emoji_command
    def slap(self, inter: discord.Interaction, target: discord.Member = None):
        "Slap someone"


async def setup(client: commands.Bot):
    "setup function of this cog."
    await client.add_cog(Emotes(client))
