"Cog for moderation commands and listeners"
import hikari
import tanjun
from configloader import config

component = tanjun.Component(name="moderation")


@component.with_slash_command
@tanjun.with_own_permission_check(hikari.Permissions.MANAGE_CHANNELS)
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_CHANNELS)
@tanjun.with_bool_slash_option(
    "static_value", "The static value to set NSFW to.", default=None
)
@tanjun.as_slash_command("nsfw", "Toggle the channel to NSFW mode.")
async def nsfw_command(ctx: tanjun.abc.Context, static_value: bool | None):
    """Toggle the channel to nsfw mode."""
    channel = await ctx.fetch_channel()

    if not isinstance(channel, hikari.GuildTextChannel):
        await ctx.respond("This command can only be used in a server text channel.")
        return

    new_value = static_value if static_value is not None else not channel.is_nsfw

    await channel.edit(nsfw=new_value)
    await ctx.respond(
        config["dialogs"]["nsfw"]["response"].format(
            channel=channel.mention, status=new_value
        )
    )


@component.with_slash_command
@tanjun.with_own_permission_check(hikari.Permissions.MANAGE_CHANNELS)
@tanjun.with_author_permission_check(hikari.Permissions.MANAGE_CHANNELS)
@tanjun.with_int_slash_option(
    "seconds", "The number of seconds for the slowdown.", min_value=0, max_value=21600
)
@tanjun.as_slash_command("slowdown", "Slows down the chat. (0 disables this)")
async def slowdown_command(ctx: tanjun.abc.Context, seconds: int):
    """Slows down the chat. (0 disables this)"""
    channel = await ctx.fetch_channel()

    if not isinstance(channel, hikari.GuildTextChannel):
        await ctx.respond("This command can only be used in a server text channel.")
        return

    await channel.edit(slow_mode_cooldown=seconds)
    await ctx.respond("Successfully changed slowmode settings.")


@tanjun.as_loader
def load_component(client: tanjun.Client):
    "Loads the moderation component."
    client.add_component(component.copy())
