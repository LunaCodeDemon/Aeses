"This module contains functions to filter certain elements"

import re
from functools import lru_cache
import logging
import emoji
import discord

from scripts.sqldata import FilterType, get_filterconfig


@lru_cache(maxsize=5)
def check_for_links(text: str) -> bool:
    "Returns true if a link exists in the string."
    regex = r"(https?:\/\/)?\w+(\.\w+)+(\/+[^\s]+)*\/?"
    return None is not re.search(regex, text)


@lru_cache(maxsize=10)
def check_for_emoji(text: str) -> bool:
    "Searches for emoji in string and returns true if emoji is found."
    for symbol in text:
        if emoji.is_emoji(symbol):
            return True
    return False


def check_text(text: str, filter_types: list[FilterType]) -> bool:
    "Check a message for potential threats."
    if FilterType.LINK in filter_types and check_for_links(text):
        return True
    return False


async def check_message(message: discord.Message) -> bool:
    "Check message for filtered text and delete it."
    if not message.guild:
        return

    filterconfigs = get_filterconfig(message.guild.id)
    if not filterconfigs:
        return
    filter_types = [f.filter_type for f in filterconfigs if f.active]
    if len(filter_types) == 0:
        return

    if check_text(message.content, filter_types):
        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            logging.exception("Deletion of filtered message failed.")
        return True
    return False


def check_nickname(member: discord.Member) -> bool:
    "Check a name for potential threats."
    filterconfigs = get_filterconfig(member.guild.id)
    if not filterconfigs:
        return
    filter_types = [f.filter_type for f in filterconfigs if f.active]
    if len(filter_types) == 0:
        return

    if member.display_name is not None:
        if FilterType.EMOJI_NAME in filter_types and check_for_emoji(member.display_name):
            return True
        if FilterType.LINK in filter_types and check_for_links(member.display_name):
            return True
    return False
