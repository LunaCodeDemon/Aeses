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
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def nsfw(self, ctx: commands.Context, static_value: bool = None):
        "Toggle the channel to nsfw mode."
        channel: discord.TextChannel = ctx.channel

        if static_value is None:
            static_value = not channel.is_nsfw()

        await channel.edit(nsfw=static_value)
        await ctx.send(config['dialogs']['nsfw']['response']
                       .format(channel=channel.mention, status=channel.is_nsfw()))


async def setup(client: commands.Bot):
    "Setup function for the moderation extention."
    await client.add_cog(Moderation(client))
