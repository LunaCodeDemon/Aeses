"""
Cog module for automations.
This includes reminder and dailies
"""
import discord
from discord import app_commands
# pylint: disable=unused-import
from discord.ext import commands, tasks
from scripts.logmessagebuilders import create_moderation_embed, create_welcome_embed
from scripts import sqldata


class Automation(commands.Cog):
    "Cog for automations like reminder and dailies"

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        "This gets triggered if the bot is ready"
        # pylint: disable=no-member
        # await self.reminder_update.start()
        # await self.daily_update.start()

    async def cog_unload(self) -> None:
        # pylint: disable=no-member
        # await self.reminder_update.stop()
        # await self.daily_update.stop()
        await super().cog_unload()

    # @tasks.loop(seconds=1)
    # async def reminder_update(self):
    #     pass  # TODO: implement reminder

    # @tasks.loop(hours=24)
    # async def daily_update(self):
    #     pass  # TODO: implement daily

    @commands.hybrid_group()
    @commands.guild_only()
    async def log(self, ctx: commands.Context):
        "Command group of log functions"
        await ctx.send_help('log')

    # FIXME check for permission
    @log.command(name="add")
    @commands.guild_only()
    @app_commands.choices(
        logtype=[
            app_commands.Choice(name="Welcome messages",
                                value=sqldata.LogType.WELCOME.value),
            app_commands.Choice(name="Moderations events",
                                value=sqldata.LogType.MODERATION.value)
        ]
    )
    async def log_add(self, ctx: commands.Context,
                      logtype: str, channel: discord.TextChannel = None):
        "Add a log channel to the list."
        if not channel:
            channel = ctx.channel
        ltype = sqldata.LogType(logtype)
        sqldata.insert_logchannel(channel.guild.id, channel.id, ltype)
        await ctx.send(f"Activated {logtype} channel.")

    @log.command(name="list")
    @commands.guild_only()
    async def log_list(self, ctx: commands.Context):
        "List active log channels."
        channels = sqldata.get_logchannel(ctx.guild.id)
        if not channels:
            await ctx.send("No log channels selected.")
            return

        embed = discord.Embed(title="Active log channels.")
        for logchannel in channels:
            embed.add_field(
                name=logchannel.logtype.name,
                value=f"<#{logchannel.channel_id}>"
            )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        "Handles member joins."
        log_channel_data = sqldata.get_logchannel(
            member.guild.id, sqldata.LogType.WELCOME)[0]

        if not log_channel_data:
            return

        channel = member.guild.get_channel(log_channel_data.channel_id)

        text = "Welcome {member} to our nice corner."
        embed = await create_welcome_embed(member, text)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        "React when a member leaves or gets kicked"
        # pylint: disable=unnecessary-dunder-call
        audit_entry: discord.AuditLogEntry = await member.guild.audit_logs(limit=1).__anext__()

        # TODO leave message

        if audit_entry.target.id != member.id:
            return

        if audit_entry.action == discord.AuditLogAction.kick:
            kick_log_channel_data = sqldata.get_logchannel(
                member.guild.id, sqldata.LogType.MODERATION)
            if kick_log_channel_data:
                kick_log_channel = member.guild.get_channel(
                    kick_log_channel_data[0].channel_id)
                embed = await create_moderation_embed(member, "kick",
                                                      audit_entry.reason or "No reason given")
                await kick_log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        "React on ban."
        reason = "No reason found"
        # pylint: disable=unnecessary-dunder-call
        audit_entry: discord.AuditLogEntry = await guild.audit_logs(limit=1).__anext__()
        if audit_entry.action == discord.AuditLogAction.ban and audit_entry.target.id == user.id:
            reason = audit_entry.reason or "No reason given"

        ban_log_channel_data = sqldata.get_logchannel(
            guild.id, sqldata.LogType.MODERATION)
        if ban_log_channel_data:
            ban_log_channel = guild.get_channel(
                ban_log_channel_data[0].channel_id)
            embed = await create_moderation_embed(user, "ban", reason)
            await ban_log_channel.send(embed=embed)


async def setup(client: commands.Bot):
    "The usual setup function."
    await client.add_cog(Automation(client))
