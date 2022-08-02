"This Cog lets server moderators change settings for the guild."
from discord import TextChannel, Permissions
from discord.ext import commands
from iniloader import config

from scripts.sqldata import insert_logchannel

class Settings(commands.Cog):
    "Moderative group to set guild settings."
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command()
    async def logchannel(self, ctx: commands.Context, *, log_channel: TextChannel):
        "Sets a logging channel."
        if ctx.channel is not TextChannel:
            await ctx.send("This command can only be used in guild channels.")

        if log_channel:
            perms: Permissions = ctx.author.permissions_for(self)
            if perms.administrator:
                insert_logchannel(ctx.guild.id, log_channel.id)
                await ctx.send(config['dialog_logchannel']['response']
                    .format(mention=log_channel.mention))
            else:
                await ctx.send(config['dialog_logchannel']['on_missing_permission']
                    .format(mention=log_channel.mention))
        else:
            await ctx.send_help("logchannel")

def setup(client: commands.Bot):
    "Setup function for settings COG"
    client.add_cog(Settings(client))
