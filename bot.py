"Bot client module, contains configuration of bot and simple listeners."

import logging
from http.client import HTTPException
import os
import discord
from discord.ext import commands
from scripts.conversion import str2only_ascii
from scripts.textfilter import check_nickname, check_message
from scripts.errors import error_dictionary

class AesesBot(commands.Bot):
    async def load_modules_from_folder(self, folder: str):
        "Loads modules from a folder."
        for file in os.listdir(folder):
            if file.endswith('.py') and file != "__init__.py":
                module_path = f"{folder}.{os.path.splitext(file)[0]}"
                await client.load_extension(module_path)
    
    async def setup_hook(self) -> None:
        await client.tree.sync()


client = AesesBot(command_prefix="!", intents=discord.Intents.all())


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
    if await check_message(message):
        return

    await client.process_commands(message)


@client.event
async def on_message_edit(_: discord.Message, updated: discord.Message):
    "This will be triggered whenever a user edits a message."
    if updated.author == client.user:
        return

    # filter
    if await check_message(updated):
        return


@client.event
async def on_member_update(_: discord.Member, after: discord.Member):
    "React on updates of the member"
    client_member: discord.Member = await after.guild.fetch_member(client.user.id)
    if client_member.guild_permissions.manage_nicknames and check_nickname(after):
        try:
            if after.nick is None:
                await after.edit(nick=str2only_ascii(after.display_name))
            else:
                await after.edit(nick=None)
        except (discord.Forbidden, HTTPException) as err:
            logging.exception(err)


@client.event
async def on_command_error(ctx: commands.Context, error: BaseException):
    "Handles errors for every command."
    if isinstance(error, commands.CommandInvokeError):
        error = error.original

    exc_func = error_dictionary.get(error)
    if exc_func:
        exc_func(ctx, error)
    else:
        logging.exception(error)
        raise error
