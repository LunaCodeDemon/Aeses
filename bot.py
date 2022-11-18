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

DEFAULT_PREFIX = os.environ.get("PREFIX", "!")
ACTIVITY_OVERWRITE = os.environ.get("ACTIVITY_OVERWRITE")

activities: List[Callable[[discord.Client], None]] = [
    # show the amount of users the bot listens to
    lambda client: discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{len(client.users)} users"),
    # show the amount of guilds the bot listens to
    lambda client: discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{len(client.guilds)} guilds"),
]


class AesesBot(commands.Bot):
    "Custom class for Aeses bot"
    async def load_modules_from_folder(self, folder: str):
        "Loads modules from a folder."
        # go through every file in the folder.
        for file in os.listdir(folder):
            # check if it's a python module
            if file.endswith('.py') and file != "__init__.py":
                # create module path
                module_path = f"{folder}.{os.path.splitext(file)[0]}"

                # load the extension using the module path.
                await client.load_extension(module_path)

    async def setup_hook(self) -> None:
        await client.tree.sync()

    @tasks.loop(minutes=15)
    async def loop_status(self):
        "Loops through few possible statuses"
        if not ACTIVITY_OVERWRITE:
            # pick a status for the bot
            await self.change_presence(activity=choice(activities)(self))
        else:
            # show the status that is written in the ACTIVITY_OVERWRITE enviroment variable.
            await self.change_presence(activity=discord.Activity(
                type=discord.ActivityType.custom,
                name=ACTIVITY_OVERWRITE
            ))

    @loop_status.before_loop
    async def before_loop_status(self):
        "Runs before status loop"
        if not self.is_ready():
            self.wait_until_ready()

    async def on_ready(self):
        "This event will be triggered when the client is ready to use."
        print(f"Discord client logged in as {client.user.name}")

        await self.set_default_profile_picture("default-profile.png")

        # pylint: disable=no-member
        self.loop_status.start()

    def add_context_menus(self, menus: List[app_commands.ContextMenu]):
        "Adds an array of context menus"
        for menu in menus:
            self.tree.add_command(menu)

    # pylint: disable=arguments-differ
    async def on_message(self, message: discord.Message):
        "This will be triggered whenever a user sends a message."
        if message.author == client.user:
            return

        # filter
        if await check_message(message):
            return

        await client.process_commands(message)

    async def on_message_edit(self, _: discord.Message, updated: discord.Message):
        "This will be triggered whenever a user edits a message."
        if updated.author == client.user:
            return

        # filter
        if await check_message(updated):
            return

    async def on_member_update(self, _: discord.Member, after: discord.Member):
        "React on updates of the member"
        client_member: discord.Member = await after.guild.fetch_member(client.user.id)

        # check the user if the client has the permission to change the nickname.
        if client_member.guild_permissions.manage_nicknames and check_nickname(after):
            try:
                # try to change the nickname depending on if the member already has a nick.
                if after.nick is None:
                    await after.edit(nick=str2only_ascii(after.display_name))
                else:
                    await after.edit(nick=None)

            except (discord.Forbidden, HTTPException) as err:
                logging.exception(err)

    async def set_profile_picture(self, path: str):
        "Change the profile picture of the bot."
        logging.info("changing profile picture to {path}", path=path)
        with open(path, "rb") as file:
            await self.user.edit(avatar=file.read())

    async def set_default_profile_picture(self, path: str):
        "Changes the profile picture if none is set yet."
        if not self.user:
            return

        # if the bot does not have an avatar, set it to the default.
        if not self.user.avatar:
            await self.set_profile_picture(path)

    async def on_command_error(self, ctx: commands.Context, error: BaseException):
        "Handles errors for every command."
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        # get an exception function
        exc_func = error_dictionary.get(error.__class__)

        # execute exception function if found.
        if exc_func:
            exc_func(ctx, error)
        else:
            logging.exception(error)


client = AesesBot(command_prefix=DEFAULT_PREFIX,
                  intents=discord.Intents.all(), help_command=None)
