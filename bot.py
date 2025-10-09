"Bot client module, contains configuration of bot and simple listeners."

import logging
import os
import asyncio
from random import choice
from typing import Callable, List
import hikari
import tanjun
import ongaku
from scripts.conversion import str2only_ascii
from scripts.textfilter import check_nickname, check_message
from scripts.errors import error_dictionary
from scripts.name_randomizer import pick_randomized_name

ACTIVITY_OVERWRITE = os.environ.get("ACTIVITY_OVERWRITE")

activities: List[Callable[[hikari.GatewayBot], hikari.Activity]] = [
    # show the amount of users the bot listens to
    lambda bot: hikari.Activity(
        type=hikari.ActivityType.LISTENING,
        name=f"{len(bot.cache.get_users_view())} users"
    ),
    # show the amount of guilds the bot listens to
    lambda bot: hikari.Activity(
        type=hikari.ActivityType.LISTENING,
        name=f"{len(bot.cache.get_guilds_view())} guilds"
    ),
    # few example commands
    lambda bot: hikari.Activity(
        type=hikari.ActivityType.LISTENING,
        name=f"/whois {pick_randomized_name()}"
    ),
    lambda bot: hikari.Activity(
        type=hikari.ActivityType.LISTENING,
        name=f"/avatar {pick_randomized_name()}"
    )
]

bot = hikari.GatewayBot(token=os.environ["DISCORD_TOKEN"], intents=hikari.Intents.ALL)
ongaku_client = ongaku.Client(bot)
client = tanjun.Client.from_gateway_bot(bot).set_type_dependency(ongaku.Client, ongaku_client)

@bot.listen(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent):
    # This is where you would connect to your lavalink node.
    # The default values are for a local lavalink node.
    await ongaku_client.create_node(
        host=os.environ.get("LAVALINK_HOST", "127.0.0.1"),
        port=int(os.environ.get("LAVALINK_PORT", 2333)),
        password=os.environ.get("LAVALINK_PASSWORD", "youshallnotpass"),
        ssl=os.environ.get("LAVALINK_SSL", "False").lower() == "true",
    )

@bot.listen(hikari.StartedEvent)
async def on_started(event: hikari.StartedEvent):
    "This event will be triggered when the client is ready to use."
    print(f"Discord client logged in as {bot.get_me().username}")
    await set_default_profile_picture("default-profile.png")
    # pylint: disable=no-member
    bot.create_task(loop_status())

async def loop_status():
    "Loops through few possible statuses"
    while True:
        if not ACTIVITY_OVERWRITE:
            # pick a status for the bot
            await bot.update_presence(activity=choice(activities)(bot))
        else:
            # show the status that is written in the ACTIVITY_OVERWRITE enviroment variable.
            await bot.update_presence(activity=hikari.Activity(
                type=hikari.ActivityType.CUSTOM, name=ACTIVITY_OVERWRITE))
        await asyncio.sleep(15 * 60)

@bot.listen(hikari.GuildMessageCreateEvent)
async def on_message(event: hikari.GuildMessageCreateEvent):
    "This will be triggered whenever a user sends a message."
    if event.author.is_bot:
        return

    # filter
    if await check_message(event.message):
        return

@bot.listen(hikari.GuildMessageUpdateEvent)
async def on_message_edit(event: hikari.GuildMessageUpdateEvent):
    "This will be triggered whenever a user edits a message."
    if event.author.is_bot:
        return

    # filter
    if await check_message(event.message):
        return

@bot.listen(hikari.MemberUpdateEvent)
async def on_member_update(event: hikari.MemberUpdateEvent):
    "React on updates of the member"
    me = await event.app.rest.fetch_my_user()
    my_member = bot.cache.get_member(event.guild_id, me.id)

    # check the user if the client has the permission to change the nickname.
    if my_member.get_permissions() & hikari.Permissions.MANAGE_NICKNAMES and check_nickname(event.member):
        try:
            # try to change the nickname depending on if the member already has a nick.
            if event.member.nickname is None:
                await event.member.edit(nick=str2only_ascii(event.member.display_name))
            else:
                await event.member.edit(nick=None)
        except (hikari.ForbiddenError, hikari.HTTPError) as err:
            logging.exception(err)

async def set_profile_picture(path: str):
    "Change the profile picture of the bot."
    logging.info("changing profile picture to {path}", path=path)
    with open(path, "rb") as file:
        await bot.rest.edit_my_user(avatar=file.read())

async def set_default_profile_picture(path: str):
    "Changes the profile picture if none is set yet."
    me = bot.get_me()
    if not me:
        return

    # if the bot does not have an avatar, set it to the default.
    if not me.avatar_hash:
        await set_profile_picture(path)

@client.with_hooks(tanjun.hooks.CommandHook(on_error=lambda ctx, err: logging.exception(err) if not error_dictionary.get(err.__class__)(ctx, err) else None))
@tanjun.as_loader
def load_components(client: tanjun.Client):
    "Loads all components from the cogs directory."
    path = "cogs"
    for file in os.listdir(path):
        if file.endswith(".py") and not file.startswith("__"):
            client.load_modules(f"{path}.{file[:-3]}")