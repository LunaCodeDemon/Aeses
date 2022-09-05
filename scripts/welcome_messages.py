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
