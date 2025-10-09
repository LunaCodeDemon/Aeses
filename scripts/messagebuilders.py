"Helper functions for welcome messages"
from typing import List
import hikari
from scripts.sqldata import FilterType


async def create_welcome_embed(member: hikari.Member, text: str) -> hikari.Embed:
    "Creates a welcome embed"
    return hikari.Embed(
        title=f"Welcome {member.username} to {member.get_guild().name}",
        description=text.format(member=member.mention, guild=member.get_guild().name)
    )


async def create_moderation_embed(user: hikari.User, action: str, reason: str) -> hikari.Embed:
    "Creates an embed for moderation stuff."
    return hikari.Embed(
        title=f"[{action.upper()}]: {user.username}",
        description=reason
    )


def generate_filtertype_listing(filters: List[FilterType]) -> str:
    "Generate a string from multiple filtertypes."
    result = "\n".join([f"- {ft.value}" for ft in filters])

    return result or "none"