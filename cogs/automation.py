"""
Cog module for automations.
This includes reminder and dailies
"""
from ctypes import Union
from datetime import datetime
import logging
from typing import List
import numpy
import discord
from discord import app_commands
# pylint: disable=unused-import
from discord.ext import commands, tasks
from scripts.messagebuilders import create_moderation_embed, create_welcome_embed
from scripts import sqldata


class Automation(commands.Cog):
    "Cog for automations like reminder and dailies"

    reminders: List[sqldata.Reminder] = None

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.reminders = []

    @commands.Cog.listener()
    async def on_ready(self):
        "This gets triggered if the bot is ready"
        # no-member has to be disabled, since pylint has confuses tasks with normal functions.
        # pylint: disable=no-member
        await self.reminder_update.start()
        # await self.daily_update.start()

    async def cog_unload(self) -> None:
        # no-member has to be disabled, since pylint has confuses tasks with normal functions.
        # pylint: disable=no-member
        await self.reminder_update.stop()
        # await self.daily_update.stop()
        await super().cog_unload()

    # it cannot be prevented that this command has a lot of options.
    @app_commands.command()
    @app_commands.guild_only()
    # pylint: disable=too-many-arguments
    async def reminder(self, inter: discord.Interaction, note: str,
                       seconds: int):
        """
            (Instable) You can set a reminder that will send you a message in a given time.
        """
        await inter.response.defer(ephemeral=True, thinking=True)
        timestamp = numpy.datetime64(datetime.now())

        added_time = numpy.timedelta64(seconds, "s")
        if added_time <= 0:
            await inter.followup.send("There is no time given for the reminder.", ephemeral=True)
            return

        trigger_time = timestamp + added_time

        rem = sqldata.Reminder(note, inter.user.id, inter.guild_id,
                               inter.channel_id, True, timestamp, trigger_time)

        self.reminders.append(rem)

        await inter.followup.send(f"Reminder scheduled for {trigger_time}", ephemeral=True)
        # TODO add reminder to database

    @tasks.loop(seconds=1)
    async def reminder_update(self):
        "Sends reminders to channels and deletes them."
        if not self.reminders:
            return
        for remind in self.reminders:
            if remind.trigger_at > numpy.datetime64(datetime.now()):
                return

            user = self.client.get_user(remind.user_id)
            target: Union[discord.TextChannel,
                          discord.User] = self.client.get_channel(remind.channel_id)
            if remind.direct:
                target = user
            if not target:
                logging.warning("Reminder without target is triggered.")
                return

            embed = discord.Embed(title="Reminder", description=remind.note)

            self.reminders.remove(remind)

            if hasattr(target, "send"):
                await target.send(user.mention, embed=embed)

        self.reminders.clear()
        # TODO: update table of reminders

    # @tasks.loop(hours=24)
    # async def daily_update(self):
    #     pass  # TODO: implement daily

    @ commands.hybrid_group()
    @ commands.guild_only()
    async def log(self, ctx: commands.Context):
        "Command group of log functions"
        await ctx.send_help('log')

    @ log.command(name="add")
    @ commands.guild_only()
    @ commands.has_permissions(administrator=True)
    @ app_commands.choices(
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

    @ log.command(name="list")
    @ commands.guild_only()
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

    @ commands.Cog.listener()
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

    @ commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        "React when a member leaves or gets kicked"
        # pylint: disable=unnecessary-dunder-call
        audit_entry: discord.AuditLogEntry = await member.guild.audit_logs(limit=1).__anext__()

        if audit_entry.target.id == member.id and audit_entry.action == discord.AuditLogAction.kick:
            kick_log_channel_data = sqldata.get_logchannel(
                member.guild.id, sqldata.LogType.MODERATION)
            if kick_log_channel_data:
                kick_log_channel = member.guild.get_channel(
                    kick_log_channel_data[0].channel_id)
                embed = await create_moderation_embed(member, "kick",
                                                      audit_entry.reason or "No reason given")
                await kick_log_channel.send(embed=embed)
        else:
            # leaving member
            pass

    @ commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        "React on ban."
        reason = "No reason found"

        # dunder linting has to be disabled, since anext() doesn't exist in v3.8
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
