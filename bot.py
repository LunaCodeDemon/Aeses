"Bot client module, contains configuration of bot and simple listeners."

import logging
from http.client import HTTPException
import os
import discord
from discord.ext import commands
from api.safebooru import SafebooruConnectionError
from scripts.textfilter import check_nickname, check_message

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
    if check_message(message):
        return

    await client.process_commands(message)

@client.event
async def on_message_edit(_: discord.Message, updated: discord.Message):
    "This will be triggered whenever a user edits a message."
    if updated.author == client.user:
        return

    # filter
    if check_message(updated):
        return

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
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    "Handles errors for every command."
    # reply the invoker is missing permissions
    if isinstance(error, commands.MissingPermissions):
        if not ctx.guild:
            await ctx.send("This command has to be called inside of a guild!")
        else:
            await ctx.send(
                "You are missing permissions to run this command.\n"
                f"Permissions that are missing: ({', '.join(error.missing_perms)})"
                )
    elif isinstance(error, commands.BotMissingPermissions):
        if not ctx.guild:
            await ctx.send("This command has to be called inside of a guild!")
        else:
            await ctx.send(
                "I do not have the right permissions to execute this command.\n"
                f"Permissions that are missing: ({', '.join(error.missing_perms)})"
                )
    elif isinstance(error, SafebooruConnectionError):
        await ctx.send("Something went wrong with the safebooru.org api.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send_help(ctx.command)
    else:
        logging.exception(error)

EXTENSION_FOLDER = 'cogs'
for file in os.listdir(EXTENSION_FOLDER):
    if file.endswith('.py') and file != "__init__.py":
        module_path = f"{EXTENSION_FOLDER}.{os.path.splitext(file)[0]}"
        client.load_extension(module_path)
