"This Cog lets server moderators change settings for the guild."
import discord
from discord import app_commands
from discord.ext import commands
# from iniloader import config

from scripts import sqldata
from scripts.messagebuilders import generate_filtertype_listing


class Settings(commands.Cog):
    "Moderative group to set guild settings."

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    # @commands.command()
    # async def logchannel(self, ctx: commands.Context, *, log_channel: TextChannel):
    #     "Sets a logging channel."
    #     if ctx.channel is not TextChannel:
    #         await ctx.send("This command can only be used in guild channels.")

    #     if log_channel:
    #         perms: Permissions = ctx.author.permissions_for(self)
    #         if perms.administrator:
    #             insert_logchannel(ctx.guild.id, log_channel.id)
    #             await ctx.send(config['dialog_logchannel']['response']
    #                 .format(mention=log_channel.mention))
    #         else:
    #             await ctx.send(config['dialog_logchannel']['on_missing_permission']
    #                 .format(mention=log_channel.mention))
    #     else:
    #         await ctx.send_help("logchannel")

    @commands.hybrid_command(aliases=["filter"])
    @commands.has_permissions(administrator=True)
    @app_commands.choices(filter_type=[
        app_commands.Choice(name="Emoji in Names", value="emona"),
        app_commands.Choice(name="Links", value="links")
    ])
    async def filterconf(self, ctx: commands.Context, filter_type: str = None, active: bool = None):
        """
            Set which filter type to enable,
            calling it without filter type lists filter types and with it will toggle the filter.
            The active parameter will allow you to set the filter directly.

            Available filter types:
            - *emona*: check for emoji in names
            - *links*: check for links in messages and names

            (The bot won't do anything if the permissions are to low.)
        """
        if not filter_type:
            filterconfig = sqldata.get_filterconfig(ctx.guild.id)

            active_filters = [
                fi.filter_type for fi in filterconfig if fi.active]

            inactive_filters = [
                fi.filter_type for fi in filterconfig if not fi.active]

            inactive_filters.extend([
                ft for ft in sqldata.FilterType
                if not ft in [*inactive_filters, *active_filters]
            ])

            active_list = generate_filtertype_listing(active_filters)
            inactive_list = generate_filtertype_listing(inactive_list)

            # create an embed to output the status of the filters.
            embed = discord.Embed()
            embed.title = "Filters"
            embed.add_field(name="Active", value=active_list)
            embed.add_field(name="Inactive", value=inactive_list)
            await ctx.send(embed=embed)
            return
        try:
            ftype = sqldata.FilterType(filter_type)
            if active is None:
                filter_active = sqldata.get_filterconfig(
                    ctx.guild.id, ftype)[0].active
                sqldata.update_filterconfig(
                    ctx.guild.id, ftype, not filter_active)
            else:
                sqldata.insert_filterconfig(ctx.guild.id, ftype, active)
            await ctx.send("Filter set and will now listen for new activity.")
        except ValueError:
            await ctx.send("Invalid filter found in arguments")


async def setup(client: commands.Bot):
    "Setup function for settings COG"
    await client.add_cog(Settings(client))
