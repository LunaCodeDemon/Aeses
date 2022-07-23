import discord
from discord.ext import commands

class Moderation(commands.Cog):
    "Moderation command group"
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @commands.command()
    async def kick(self, ctx: commands.Context, *, member: discord.Member = None):
        "This command kicks a member."
        if member:
            await ctx.send(f"{member.mention} has been kicked.")
        else:
            await ctx.send_help("warn")

def setup(client: commands.Bot):
    "Setup function for the moderation extention."
    client.add_cog(Moderation(client))
