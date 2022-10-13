"Cog for moderation commands and listeners"
from http.client import HTTPException
import discord
from discord.ext import commands
from configloader import config


class Moderation(commands.Cog):
    "Moderation command group"

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, reason: str):
        "This command kicks a member."
        try:
            await member.kick(reason=reason)
            await ctx.send(config['dialogs']['kick']['response'].format(mention=member.mention))
        except HTTPException:
            await ctx.send(config['dialogs']['kick']['on_fail'].format(mention=member.mention))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: str):
        "This command bans a member."

        try:
            await member.ban(reason=reason)
            await ctx.send(config['dialogs']['ban']['response'].format(mention=member.mention))
        except HTTPException:
            await ctx.send(config['dialogs']['ban']['on_fail'].format(mention=member.mention))

    # don't know if i should turn this into hybrid command
    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def nsfw(self, ctx: commands.Context, static_value: bool = None):
        "Toggle the channel to nsfw mode."
        channel: discord.TextChannel = ctx.channel

        # use the inverted boolean of the is_nsfw if static_value isn't given.
        if static_value is None:
            static_value = not channel.is_nsfw()

        # set the nsfw setting for the channel.
        await channel.edit(nsfw=static_value)
        await ctx.send(config['dialogs']['nsfw']['response']
                       .format(channel=channel.mention, status=channel.is_nsfw()))

    @commands.hybrid_command(aliases=["slow"])
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowdown(self, ctx: commands.Context, seconds: int):
        "Slows down the chat. (0 disables this)"
        # don't allow a negative number.
        if seconds < 0:
            await ctx.send("This command doesn't work with negative numbers")
            return

        # set the slowdown for the channel.
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send("Successfully changed slowmode settings.")


async def setup(client: commands.Bot):
    "Setup function for the moderation extention."
    await client.add_cog(Moderation(client))
