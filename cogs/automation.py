"""
Cog module for automations.
This includes reminder and dailies
"""
from datetime import datetime, timedelta
import logging
from typing import List
import numpy
import hikari
import tanjun
from scripts.messagebuilders import create_moderation_embed, create_welcome_embed
from scripts import sqldata

component = tanjun.Component(name="automation")

@component.with_slash_command
@tanjun.with_str_slash_option("note", "The note for the reminder.")
@tanjun.with_int_slash_option("seconds", "The number of seconds from now to set the reminder for.", min_value=1)
@tanjun.as_slash_command("reminder", "(Instable) Set a reminder that will send you a message in a given time.")
async def reminder_command(ctx: tanjun.abc.Context, note: str, seconds: int):
    """(Instable) You can set a reminder that will send you a message in a given time."""
    await ctx.defer(ephemeral=True)

    timestamp = numpy.datetime64(datetime.now())
    trigger_time = timestamp + numpy.timedelta64(seconds, "s")

    rem = sqldata.Reminder(
        note=note,
        user_id=ctx.author.id,
        guild_id=ctx.guild_id,
        channel_id=ctx.channel_id,
        direct=True,  # Assuming direct message for simplicity, can be changed.
        created_at=timestamp,
        trigger_at=trigger_time
    )

    sqldata.insert_reminder(rem)

    await ctx.create_followup(f"Reminder scheduled for {trigger_time}", ephemeral=True)

log_group = tanjun.slash_command_group("log", "Commands for logging purposes")
component.add_slash_command(log_group)

@tanjun.with_str_slash_option("logtype", "The type of log to add.", choices={
    "Welcome messages": sqldata.LogType.WELCOME.value,
    "Moderation events": sqldata.LogType.MODERATION.value
})
@tanjun.with_channel_slash_option("channel", "The channel to set as the log channel.", default=None)
@tanjun.with_author_permission_check(hikari.Permissions.ADMINISTRATOR)
@log_group.as_sub_command("add", "Add a log channel to the list.")
async def log_add_command(ctx: tanjun.abc.Context, logtype: str, channel: hikari.InteractionChannel | None):
    """Add a log channel to the list."""
    target_channel = channel or await ctx.fetch_channel()
    ltype = sqldata.LogType(logtype)
    sqldata.insert_logchannel(ctx.guild_id, target_channel.id, ltype)
    await ctx.respond(f"Activated {logtype} channel.")

@log_group.as_sub_command("list", "List active log channels.")
async def log_list_command(ctx: tanjun.abc.Context):
    """List active log channels."""
    channels = sqldata.get_logchannel(ctx.guild_id)
    if not channels:
        await ctx.respond("No log channels selected.")
        return

    embed = hikari.Embed(title="Active log channels.")
    for logchannel in channels:
        embed.add_field(name=logchannel.logtype.name, value=f"<#{logchannel.channel_id}>")
    await ctx.respond(embed=embed)

@component.with_schedule
@tanjun.as_interval(timedelta(seconds=1))
async def reminder_update(bot: hikari.GatewayBot = tanjun.inject()):
    """Sends reminders to channels and deletes them."""
    timestamp = datetime.now()
    reminders = sqldata.restore_reminders()

    if not reminders:
        return

    reminders_to_process = [r for r in reminders if numpy.datetime64(r.trigger_at) <= numpy.datetime64(timestamp)]

    if not reminders_to_process:
        return

    for remind in reminders_to_process:
        try:
            user = await bot.rest.fetch_user(remind.user_id)
            target = await bot.rest.fetch_channel(remind.channel_id)

            if not target:
                logging.warning(f"Reminder target channel {remind.channel_id} not found.")
                continue

            embed = hikari.Embed(title="Reminder", description=remind.note)
            await target.send(user.mention, embed=embed)

        except (hikari.ForbiddenError, hikari.NotFoundError) as e:
            logging.warning(f"Could not send reminder {remind.id}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while processing reminder {remind.id}: {e}")

    sqldata.cleanup_reminders(timestamp)

@component.with_listener(hikari.MemberJoinEvent)
async def on_member_join(event: hikari.MemberJoinEvent, bot: hikari.GatewayBot = tanjun.inject()):
    """Handles member joins."""
    log_channel_data = sqldata.get_logchannel(event.guild_id, sqldata.LogType.WELCOME)
    if not log_channel_data:
        return

    channel = await bot.rest.fetch_channel(log_channel_data[0].channel_id)
    text = "Welcome {member} to our nice corner."
    embed = await create_welcome_embed(event.member, text)
    await channel.send(embed=embed)

@component.with_listener(hikari.MemberLeaveEvent)
async def on_member_leave(event: hikari.MemberLeaveEvent, bot: hikari.GatewayBot = tanjun.inject()):
    """React when a member leaves or gets kicked"""
    try:
        async for entry in bot.rest.fetch_audit_log(
            guild=event.guild_id,
            action_type=hikari.AuditLogEventType.MEMBER_KICK
        ).limit(1):
            if entry.target == event.user:
                log_channel_data = sqldata.get_logchannel(event.guild_id, sqldata.LogType.MODERATION)
                if log_channel_data:
                    channel = await bot.rest.fetch_channel(log_channel_data[0].channel_id)
                    embed = await create_moderation_embed(event.user, "kick", entry.reason or "No reason given")
                    await channel.send(embed=embed)
                return
    except hikari.ForbiddenError:
        logging.warning(f"Missing permissions to fetch audit log in guild {event.guild_id}")
    # This is a leave event, not a kick. Handle if necessary.

@component.with_listener(hikari.BanCreateEvent)
async def on_member_ban(event: hikari.BanCreateEvent, bot: hikari.GatewayBot = tanjun.inject()):
    """React on ban."""
    reason = "No reason found"
    try:
        async for entry in bot.rest.fetch_audit_log(
            guild=event.guild_id,
            action_type=hikari.AuditLogEventType.MEMBER_BAN_ADD
        ).limit(1):
            if entry.target == event.user:
                reason = entry.reason or "No reason given"
                break
    except hikari.ForbiddenError:
        logging.warning(f"Missing permissions to fetch audit log in guild {event.guild_id}")

    log_channel_data = sqldata.get_logchannel(event.guild_id, sqldata.LogType.MODERATION)
    if log_channel_data:
        channel = await bot.rest.fetch_channel(log_channel_data[0].channel_id)
        embed = await create_moderation_embed(event.user, "ban", reason)
        await channel.send(embed=embed)

@tanjun.as_loader
def load_component(client: tanjun.Client):
    "Loads the automation component."
    sqldata.create_table_reminder()
    client.add_component(component.copy())