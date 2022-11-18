"Helper functions for welcome messages"
from typing import List
import discord
from scripts.sqldata import FilterType
from api.safebooru import SafebooruPost

async def create_welcome_embed(member: discord.Member, text: str):
    "Creates a welcome embed"
    return discord.Embed(title=f"Welcome {member.name} to {member.guild.name}",
                         description=text.format(
                             member=member.mention,
                             guild=member.guild.name
                         )
                         )


async def create_moderation_embed(user: discord.User, action: str, reason: str):
    "Creates an embed for moderation stuff."
    return discord.Embed(
        title=f"[{action}]: {user.name}",
        description=reason
    )


def generate_filtertype_listing(filters: List[FilterType]):
    "Generate a string from multiple filtertypes."
    result = "\n".join([f"- {ft.value}" for ft in filters])
    return result or "none"

def generate_booru_message(post: SafebooruPost):
    """
        Generate a message for a booru post.
    """
    embed = discord.Embed()
    embed.title = f"Post: {post.post_id}"
    embed.description = f"You will find the post here: {post.post_url}"
    embed.set_footer(
        text="Post has comments" if post.has_comments else "Post has no comments.")
    embed.set_image(url=post.file_url)
    return embed
