"""Bot client module, contains configuration of bot and simple listeners."""

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
from scripts.name_randomizer import pick_randomized_name

ACTIVITY_OVERWRITE = os.environ.get("ACTIVITY_OVERWRITE")

activities: List[Callable[[hikari.GatewayBot], hikari.Activity]] = [
    lambda bot: hikari.Activity(
        type=hikari.ActivityType.LISTENING, name=f"{len(bot.cache.get_users_view())} users"
    ),
    lambda bot: hikari.Activity(
        type=hikari.ActivityType.LISTENING, name=f"{len(bot.cache.get_guilds_view())} guilds"
    ),
    lambda bot: hikari.Activity(
        type=hikari.ActivityType.LISTENING, name=f"/whois {pick_randomized_name()}"
    ),
    lambda bot: hikari.Activity(
        type=hikari.ActivityType.LISTENING, name=f"/avatar {pick_randomized_name()}"
    ),
]

def build_bot() -> hikari.GatewayBot:
    """Build the bot object."""
    bot = hikari.GatewayBot(token=os.environ["DISCORD_TOKEN"], intents=hikari.Intents.ALL)
    ongaku_client = ongaku.Client(bot)

    (
        tanjun.Client.from_gateway_bot(bot)
        .set_type_dependency(ongaku.Client, ongaku_client)
        .load_modules(
            "cogs.automation",
            "cogs.emotes",
            "cogs.fun",
            "cogs.moderation",
            "cogs.music",
            "cogs.settings",
            "cogs.utility",
        )
    )

    return bot

bot = build_bot()

@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    """Event that is triggered when the bot is starting."""
    # This is where you would connect to your lavalink node.
    # The default values are for a local lavalink node.
    ongaku_client = bot.get_injection_context().get_key(ongaku.Client)
    await ongaku_client.create_node(
        host=os.environ.get("LAVALINK_HOST", "127.0.0.1"),
        port=int(os.environ.get("LAVALINK_PORT", 2333)),
        password=os.environ.get("LAVALINK_PASSWORD", "youshallnotpass"),
        ssl=os.environ.get("LAVALINK_SSL", "False").lower() == "true",
    )

@bot.listen(hikari.StartedEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    """This event will be triggered when the client is ready to use."""
    print(f"Discord client logged in as {bot.get_me().username}")
    await set_default_profile_picture("default-profile.png")
    bot.create_task(loop_status())

async def loop_status() -> None:
    """Loops through few possible statuses."""
    while True:
        if not ACTIVITY_OVERWRITE:
            await bot.update_presence(activity=choice(activities)(bot))
        else:
            await bot.update_presence(
                activity=hikari.Activity(
                    type=hikari.ActivityType.CUSTOM, name=ACTIVITY_OVERWRITE
                )
            )
        await asyncio.sleep(15 * 60)

@bot.listen()
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    """This will be triggered whenever a user sends a message."""
    if event.author.is_bot:
        return

    if await check_message(event.message):
        return

@bot.listen()
async def on_message_edit(event: hikari.GuildMessageUpdateEvent) -> None:
    """This will be triggered whenever a user edits a message."""
    if event.author.is_bot:
        return

    if await check_message(event.message):
        return

@bot.listen()
async def on_member_update(event: hikari.MemberUpdateEvent) -> None:
    """React on updates of the member."""
    me = await event.app.rest.fetch_my_user()
    my_member = bot.cache.get_member(event.guild_id, me.id)

    if (
        my_member
        and my_member.get_permissions() & hikari.Permissions.MANAGE_NICKNAMES
        and check_nickname(event.member)
    ):
        try:
            if event.member.nickname is None:
                await event.member.edit(nick=str2only_ascii(event.member.display_name))
            else:
                await event.member.edit(nick=None)
        except (hikari.ForbiddenError, hikari.HTTPError) as err:
            logging.exception(err)

async def set_profile_picture(path: str) -> None:
    """Change the profile picture of the bot."""
    logging.info("changing profile picture to %s", path)
    with open(path, "rb") as file:
        await bot.rest.edit_my_user(avatar=file.read())

async def set_default_profile_picture(path: str) -> None:
    """Changes the profile picture if none is set yet."""
    me = bot.get_me()
    if not me:
        return

    if not me.avatar_hash:
        await set_profile_picture(path)