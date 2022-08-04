"Bot client module, contains configuration of bot and simple listeners."

import logging
from http.client import HTTPException
import os
import discord
from discord.ext import commands
from scripts.textfilter import check_nickname, check_text

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@client.event
async def on_ready():
    "This event will be triggered when the client is ready to use."
    print(f"Discord client logged in as {client.user.name}")

@client.event
async def on_message(message: discord.Message):
    "This will be triggered whenever a user sends a message."
    if message.author == client.user:
        return

    # filter
    if check_text(message.content):
        try:
            message.delete()
        except (discord.Forbidden, discord.NotFound, HTTPException):
            logging.exception("Deletion of filtered message failed.")

        return

    await client.process_commands(message)

@client.event
async def on_message_edit(_: discord.Message, updated: discord.Message):
    "This will be triggered whenever a user edits a message."
    if updated.author == client.user:
        return

    # filter
    if check_text(updated.content):
        try:
            updated.delete()
        except (discord.Forbidden, discord.NotFound, HTTPException):
            logging.exception("Deletion of filtered message failed.")

@client.event
async def on_member_update(_: discord.Member, after: discord.Member):
    "React on updates of the member"
    if check_nickname(after):
        try:
            await after.edit(nick=None)
            await after.send("Your nickname got removed.")
        except (discord.Forbidden, HTTPException) as err:
            logging.exception(err)

@client.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
    "React if a member got banned."
    logging.info("%s got banned from guild %s.", user.name, guild.name)
    # TODO send a message in logchannel if configured

@client.event
async def on_member_remove(member: discord.Member):
    "React if a member got removed/kicked."
    guild: discord.Guild = member.guild
    kick_entry: discord.AuditLogEntry

    try:
        kick_entry = await guild.audit_logs(
            user=member,
            action=discord.AuditLogAction.kick
            ).flatten()[0]
    except discord.Forbidden:
        logging.warning("wasn't able to log in guild %s with id %d", guild.name, guild.id)
        return

    if kick_entry:
        logging.info("%s got kicked from guild %s.", member.name, guild.name)
        # TODO send a message in logchannel if configured


EXTENSION_FOLDER = 'cogs'
for file in os.listdir(EXTENSION_FOLDER):
    if file.endswith('.py') and file != "__init__.py":
        module_path = f"{EXTENSION_FOLDER}.{os.path.splitext(file)[0]}"
        client.load_extension(module_path)
