"This module contains functions to filter certain elements"

import re
from functools import lru_cache
from typing import List
import logging
import emoji
import hikari

from scripts.sqldata import FilterType, get_filterconfig


def get_active_filters(guild_id: int) -> List[FilterType]:
    "Get only the active filters"
    filterconfigs = get_filterconfig(guild_id)

    if not filterconfigs:
        return []

    return [f.filter_type for f in filterconfigs if f.active]


@lru_cache(maxsize=5)
def check_for_links(text: str) -> bool:
    "Returns true if a link exists in the string."
    if not text:
        return False
    regex = r"(https?:\/\/)?\w+(\.\w+)+(\/+[^\s]+)*\/?"
    return re.search(regex, text) is not None


@lru_cache(maxsize=10)
def check_for_emoji(text: str) -> bool:
    "Searches for emoji in string and returns true if emoji is found."
    if not text:
        return False
    # return true if there is an emoji in the string.
    for symbol in text:
        if emoji.is_emoji(symbol):
            return True

    return False


def check_text(text: str, filter_types: List[FilterType]) -> bool:
    "Check a message for potential threats."
    if FilterType.LINK in filter_types and check_for_links(text):
        return True
    return False


async def check_message(message: hikari.Message) -> bool:
    "Check message for filtered text and delete it."
    if not message.guild_id or not message.content:
        return False

    # exctact only the active filters.
    filter_types = get_active_filters(message.guild_id)

    # if there is none active, going further wouldn't make a difference.
    if not filter_types:
        return False

    # use check_text to check the message.
    if check_text(message.content, filter_types):
        try:
            await message.delete()
        except (hikari.ForbiddenError, hikari.NotFoundError, hikari.HTTPError):
            logging.exception("Deletion of filtered message failed.")
        return True
    return False


def check_nickname(member: hikari.Member) -> bool:
    "Check a name for potential threats."
    # exctact only the active filters.
    filter_types = get_active_filters(member.guild_id)

    if not filter_types:
        return False

    if member.display_name:
        # check for an emoji in the name
        if FilterType.EMOJI_NAME in filter_types and check_for_emoji(
                member.display_name):
            return True

        # check for a link in the name
        if FilterType.LINK in filter_types and check_for_links(
                member.display_name):
            return True
    return False