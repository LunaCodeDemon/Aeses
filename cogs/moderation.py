"Cog for moderation commands and listeners"
from http.client import HTTPException
import discord
from discord.ext import commands
from iniloader import config

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
            await ctx.send(config['dialog_kick']['response'].format(mention=member.mention))
        except HTTPException:
            await ctx.send(config['dialog_kick']['on_fail'].format(mention=member.mention))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: str):
        "This command bans a member."

        try:
            await member.ban(reason=reason)
            await ctx.send(config['dialog_ban']['response'].format(mention=member.mention))
        except HTTPException:
            await ctx.send(config['dialog_ban']['on_fail'].format(mention=member.mention))

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def nsfw(self, ctx: commands.Context, set_nsfw: bool = None):
        "Toggle the channel to nsfw mode."
        channel: discord.TextChannel = ctx.channel

        if set_nsfw is None:
            set_nsfw = not channel.is_nsfw()

        await channel.edit(nsfw=set_nsfw)
        await ctx.send(config['dialog_nsfw']['response']
            .format(channel=channel.mention, status=channel.is_nsfw()))

def setup(client: commands.Bot):
    "Setup function for the moderation extention."
    client.add_cog(Moderation(client))
