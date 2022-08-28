"Bot client module, contains configuration of bot and simple listeners."

import logging
from http.client import HTTPException
import os
from random import choice
from typing import Callable, List
import discord
from discord import app_commands
from discord.ext import commands, tasks
from scripts.conversion import str2only_ascii
from scripts.textfilter import check_nickname, check_message
from scripts.errors import error_dictionary

DEFAULT_PREFIX = "!"

activities: List[Callable[[discord.Client], None]] = [
    lambda client: discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{len(client.users)} users"),
    lambda client: discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{len(client.guilds)} guilds"),
    lambda client: discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{DEFAULT_PREFIX}help"),
    lambda client: discord.Activity(
        type=discord.ActivityType.listening,
        name="/help"),
    lambda client: discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{DEFAULT_PREFIX}help"
        ),
]

class AesesBot(commands.Bot):
    "Custom class for Aeses bot"
    async def load_modules_from_folder(self, folder: str):
        "Loads modules from a folder."
        for file in os.listdir(folder):
            if file.endswith('.py') and file != "__init__.py":
                module_path = f"{folder}.{os.path.splitext(file)[0]}"
                await client.load_extension(module_path)

    async def setup_hook(self) -> None:
        await client.tree.sync()

    @tasks.loop(minutes=15)
    async def loop_status(self):
        "Loops through few possible statuses"
        await self.change_presence(activity=choice(activities)(self))

    @loop_status.before_loop
    async def before_loop_status(self):
        "Runs before status loop"
        if not self.is_ready():
            self.wait_until_ready()

    async def on_ready(self):
        "This event will be triggered when the client is ready to use."
        print(f"Discord client logged in as {client.user.name}")
        # pylint: disable=no-member
        self.loop_status.start()

    def add_context_menus(self, menus: List[app_commands.ContextMenu]):
        "Adds an array of context menus"
        for menu in menus:
            self.tree.add_command(menu)


client = AesesBot(command_prefix="!", intents=discord.Intents.all())


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


@client.event
async def on_error(error: BaseException):
    "log errors"
    logging.exception(error)
    raise error
