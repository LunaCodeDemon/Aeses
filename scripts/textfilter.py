"This module contains functions to filter certain elements"

import re
from functools import lru_cache
import emoji
import discord
import logging

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

def check_text(text: str) -> bool:
    "Check a message for potential threats."
    if check_for_links(text):
        return True
    return False

async def check_message(message: discord.Message) -> bool:
    "Check message for filtered text and delete it."
    if check_text(message.content):
        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            logging.exception("Deletion of filtered message failed.")
        finally:
            return True
    return False

def check_nickname(member: discord.Member) -> bool:
    "Check a name for potential threats."
    if member.display_name is not None:
        if check_for_emoji(member.display_name):
            return True
        if check_for_links(member.display_name):
            return True
    return False
