"Cog for moderation commands and listeners"
import discord
from discord import app_commands
from discord.ext import commands
from configloader import config


class Moderation(commands.Cog):
    "Moderation command group"

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    # don't know if i should turn this into hybrid command

    @app_commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def nsfw(self,
                   inter: discord.Interaction,
                   static_value: bool = None):
        "Toggle the channel to nsfw mode."
        channel: discord.TextChannel = inter.channel

        # use the inverted boolean of the is_nsfw if static_value isn't given.
        if static_value is None:
            static_value = not channel.is_nsfw()

        # set the nsfw setting for the channel.
        await channel.edit(nsfw=static_value)
        await inter.response.send_message(
            config['dialogs']['nsfw']['response'].format(
                channel=channel.mention, status=channel.is_nsfw()))

    @app_commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowdown(self, inter: discord.Interaction, seconds: int):
        "Slows down the chat. (0 disables this)"
        # don't allow a negative number.
        if seconds < 0:
            await inter.response.send_message(
                "This command doesn't work with negative numbers")
            return

        # set the slowdown for the channel.
        await inter.channel.edit(slowmode_delay=seconds)
        await inter.response.send_message(
            "Successfully changed slowmode settings.")


async def setup(client: commands.Bot):
    "Setup function for the moderation extention."
    await client.add_cog(Moderation(client))
