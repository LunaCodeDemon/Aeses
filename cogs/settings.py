"This Cog lets server moderators change settings for the guild."
from discord.ext import commands

class Settings(commands.Cog):
    "Moderative group to set guild settings."
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command()
    async def logchannel(self, ctx: commands.Context):
        "Sets a logging channel. (WIP)"
        await ctx.send("This command is work in progress.")

        # TODO: set log channel in database

def setup(client: commands.Bot):
    "Setup function for settings COG"
    client.add_cog(Settings(client))
