"Helper functions for welcome messages"
import discord


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
