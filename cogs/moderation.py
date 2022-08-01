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
    @commands.has_permissions(kick_member=True)
    async def kick(self, ctx: commands.Context, *, member: discord.Member, reason: str):
        "This command kicks a member."
        if member:
            try:
                await member.kick(reason=reason)
                await ctx.send(config['dialog_kick']['response'].format(mention=member.mention))
            except HTTPException:
                await ctx.send(config['dialog_kick']['on_fail'].format(mention=member.mention))
        else:
            await ctx.send_help("kick")

    @commands.command()
    @commands.has_permissions(ban_member=True)
    async def ban(self, ctx: commands.Context, *, member: discord.Member, reason: str):
        "This command kicks a member."
        if member:
            try:
                await member.ban(reason=reason)
                await ctx.send(config['dialog_ban']['response'].format(mention=member.mention))
            except HTTPException:
                await ctx.send(config['dialog_ban']['on_fail'].format(mention=member.mention))
        else:
            await ctx.send_help("ban")

def setup(client: commands.Bot):
    "Setup function for the moderation extention."
    client.add_cog(Moderation(client))
