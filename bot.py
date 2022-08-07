"Bot client module, contains configuration of bot and simple listeners."

import logging
from http.client import HTTPException
import os
import discord
from discord.ext import commands
from api.safebooru import SafebooruConnectionError, SafebooruNothingFound
from scripts.conversion import str2only_ascii
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
    try:
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        raise error from None
    # reply the invoker is missing permissions
    except commands.MissingPermissions:
        if not ctx.guild:
            await ctx.send("This command has to be called inside of a guild!")
        else:
            await ctx.send(
                "You are missing permissions to run this command.\n"
                f"Permissions that are missing: ({', '.join(error.missing_perms)})"
            )
    except commands.BotMissingPermissions:
        if not ctx.guild:
            await ctx.send("This command has to be called inside of a guild!")
        else:
            await ctx.send(
                "I do not have the right permissions to execute this command.\n"
                f"Permissions that are missing: ({', '.join(error.missing_perms)})"
            )
    except SafebooruConnectionError:
        await ctx.send("Something went wrong with the safebooru.org api.")
    except SafebooruNothingFound:
        await ctx.send(f"Couldn't find something for given tags. ({', '.join(list(error.tags))})")
    except commands.MissingRequiredArgument:
        await ctx.send_help(ctx.command)
    finally:
        logging.exception(error)

EXTENSION_FOLDER = 'cogs'
for file in os.listdir(EXTENSION_FOLDER):
    if file.endswith('.py') and file != "__init__.py":
        module_path = f"{EXTENSION_FOLDER}.{os.path.splitext(file)[0]}"
        client.load_extension(module_path)
