"This Cog lets server moderators change settings for the guild."
from discord import TextChannel, Permissions
from discord.ext import commands

from scripts.sqldata import insert_logchannel

class Settings(commands.Cog):
    "Moderative group to set guild settings."
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command()
    async def logchannel(self, ctx: commands.Context, *, log_channel: TextChannel):
        "Sets a logging channel."
        if log_channel:
            perms: Permissions = ctx.author.permissions_for(self)
            if perms.administrator:
                insert_logchannel(ctx.guild.id, log_channel.id)
                await ctx.send(f"Set {log_channel.mention} as logging channel.")
            else:
                await ctx.send("You do not have the correct permissions to do that.")
        else:
            await ctx.send_help("logchannel")

def setup(client: commands.Bot):
    "Setup function for settings COG"
    client.add_cog(Settings(client))
