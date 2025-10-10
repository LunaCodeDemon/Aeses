"""
This Module adds commands that allow listening to radio and music in guild channels.
"""
import hikari
import tanjun
import ongaku
from api import radio_browser
from scripts import textfilter

component = tanjun.Component(name="music")

@component.with_slash_command
@tanjun.with_str_slash_option("query", "A search query or a direct URL.")
@tanjun.as_slash_command("play", "Play music from a web stream or search for a radio station.")
async def play_command(
    ctx: tanjun.abc.Context,
    query: str,
    ongaku_client: ongaku.Client = tanjun.inject()
):
    """Play music from a web stream. (Only Webradio Links for now)"""
    if not ctx.member or not ctx.member.voice_state or not ctx.member.voice_state.channel_id:
        await ctx.respond("You must be in a voice channel to use this command.")
        return

    voice_state = ctx.member.voice_state

    try:
        player = await ongaku_client.create_player(ctx.guild_id)
        if not player.is_connected:
            await player.connect(voice_state.channel_id)

    except ongaku.PlayerError as e:
        await ctx.respond(f"Failed to connect to voice channel: {e}")
        return

    if textfilter.check_for_links(query):
        result = await ongaku_client.rest.load_track(query)
        if not result:
            await ctx.respond("Could not load track from the provided URL.")
            return

        try:
            await player.play(result.track)
            await ctx.respond(f"Now playing: {result.track.info.title}")
        except ongaku.PlayerException as e:
            await ctx.respond(f"Failed to play track: {e}")
        return

    # Radio station search logic
    await ctx.defer()
    stations = radio_browser.search_radio(query, limit=25)
    if not stations:
        await ctx.respond("Couldn't find any station matching your search term.")
        return

    options = [
        hikari.SelectMenuOption(label=station.name[:100], value=station.url, description=(station.tags or "No tags")[:100])
        for station in stations
    ]

    select_menu = ctx.rest.build_action_row().add_select_menu("radio_station_select")
    for option in options:
        select_menu.add_option(option)

    await ctx.create_followup(
        "Select a station:",
        component=select_menu.parent
    )

    try:
        event = await ctx.app.wait_for(
            hikari.InteractionCreateEvent,
            timeout=60,
            predicate=lambda e: (
                isinstance(e.interaction, hikari.ComponentInteraction)
                and e.interaction.custom_id == "radio_station_select"
                and e.interaction.user.id == ctx.author.id
            ),
        )
        url = event.interaction.values[0]
        result = await ongaku_client.rest.load_track(url)
        if not result:
            await ctx.edit_initial_response("Could not load track from the selected station.")
            return

        await player.play(result.track)
        await ctx.edit_initial_response(f"Now playing: {result.track.info.title}", components=[])

    except TimeoutError:
        await ctx.edit_initial_response("Selection timed out.", components=[])

@component.with_slash_command
@tanjun.as_slash_command("disconnect", "Disconnect the bot from the voice channel.")
async def disconnect_command(ctx: tanjun.abc.Context, ongaku_client: ongaku.Client = tanjun.inject()):
    """Disconnect bot from channel."""
    try:
        await ongaku_client.disconnect(ctx.guild_id)
        await ctx.respond("Disconnected from the channel.")
    except ongaku.PlayerMissingError:
        await ctx.respond("I am not connected to any voice channel in this server.")
    except Exception as e:
        await ctx.respond(f"An error occurred: {e}")

@component.with_slash_command
@tanjun.with_int_slash_option("percentage", "The volume percentage (0-100).", min_value=0, max_value=100)
@tanjun.as_slash_command("volume", "Changes the volume of the audio stream.")
async def volume_command(ctx: tanjun.abc.Context, percentage: int, ongaku_client: ongaku.Client = tanjun.inject()):
    """Changes the Volume of the Audio for the current stream."""
    try:
        player = ongaku_client.fetch_player(ctx.guild_id)
        await player.set_volume(percentage)
        await ctx.respond(f"Set stream volume to {percentage}%")
    except ongaku.PlayerMissingException:
        await ctx.respond("There is no audio stream in this guild.")
    except Exception as e:
        await ctx.respond(f"An error occurred: {e}")

@tanjun.as_loader
def load_component(client: tanjun.Client):
    "Loads the music component."
    client.add_component(component.copy())