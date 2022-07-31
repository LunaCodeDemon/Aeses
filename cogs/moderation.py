"Cog for moderation commands and listeners"
from http.client import HTTPException
import discord
from discord.ext import commands

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
                await ctx.send(f"{member.mention} has been kicked.")
            except HTTPException:
                await ctx.send("Kicking failed.")
        else:
            await ctx.send_help("kick")

def setup(client: commands.Bot):
    "Setup function for the moderation extention."
    client.add_cog(Moderation(client))
