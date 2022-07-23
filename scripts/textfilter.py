"This module contains functions to filter certain elements"

import re
import emoji
from discord import Message, Member

def check_for_links(text: str) -> bool:
    "Returns true if a link exists in the string."
    regex = r"(https?:\/\/)?\w+(\.\w+)+(\/+[^\s]+)*\/?"
    return None is not re.search(regex, text)

def check_for_emoji(text: str) -> bool:
    "Searches for emoji in string and returns true if emoji is found."
    for symbol in text:
        if emoji.is_emoji(symbol):
            return True
    return False

def check_message(message: Message) -> bool:
    "Check a message for potential threats."
    if check_for_links(message.content):
        return True
    return False

def check_nickname(member: Member) -> bool:
    "Check a name for potential threats."
    if member.nick is not None and check_for_emoji(member.nick):
        return True
    return False
