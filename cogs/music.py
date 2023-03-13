"""
    This Module adds commands that allow listening to radio and music in guild channels.
"""

from typing import NamedTuple
from typing import Dict, List
import discord
from discord import app_commands
from discord import opus
from discord import ui
from discord.ext import commands
from scripts import textfilter
from api import radio_browser


class AudioStream(NamedTuple):
    """
        Structured tuple for audio streams
    """
    url: str
    source: discord.FFmpegPCMAudio
    transform: discord.PCMVolumeTransformer
    vc: discord.VoiceClient


sources_on_guild: Dict[int, AudioStream] = {}


async def play_from_url(interaction: discord.Interaction, source_url: str):
    """
        Function that plays music inside a channel..
    """
    await interaction.response.defer(ephemeral=True)
    voice_channel = interaction.user.voice.channel

    # grab the voice client that is available.
    try:
        voice_client = await voice_channel.connect(self_deaf=True)
    except (discord.GatewayNotFound, discord.ConnectionClosed):
        voice_client = sources_on_guild.get(interaction.guild_id).vc

    # creates an audio source object
    audio_source = discord.FFmpegPCMAudio(
        source_url,
        before_options='-reconnect 1 -reconnect_streamed 1 ' +
        '-reconnect_delay_max 5',
        options='-vn')

    # creates a volume transformer object
    audio_transform = discord.PCMVolumeTransformer(audio_source)

    # saves all objects for later use.
    sources_on_guild[interaction.guild_id] = AudioStream(
        url=source_url,
        source=audio_source,
        transform=audio_transform,
        vc=voice_client)

    # play audio from the audio_transform allowing for volume changes on the fly.
    voice_client.play(audio_transform,
                      after=lambda e: sources_on_guild.pop(voice_channel.id))

    await interaction.followup.send(f"Playing music from {source_url}")


class Music(commands.Cog):
    """
        Commands that interact with music.
    """
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    class StationSelect(ui.Select):
        """
            Selection of radio station
        """
        def __init__(self,
                     *,
                     placeholder: str,
                     max_values: int = 1,
                     options: List[discord.SelectOption]) -> None:
            super().__init__(placeholder=placeholder,
                             max_values=max_values,
                             options=options)

        async def callback(self, interaction: discord.Interaction) -> None:
            await play_from_url(interaction, self.values[0])

    @app_commands.command()
    @app_commands.guild_only()
    @commands.bot_has_permissions(speak=True, connect=True)
    async def play(self, interaction: discord.Interaction, src: str):
        """
            Play music from a web stream. (Only Webradio Links for now)
        """
        source_url = src
        if not textfilter.check_for_links(src):
            await interaction.response.defer()
            options: List[discord.SelectOption] = []
            stations = radio_browser.search_radio(src)
            for station in stations:
                options.append(
                    discord.SelectOption(label=station.name,
                                         value=station.url))

            if len(options) == 0:
                await interaction.followup.send("""
                Couldn't find any station matching your search term.
                Remember that this bot, does not have youtube support for now.
                """)

            class RadioView(ui.View):
                """
                    View for selecting radio stations.
                """
                @discord.ui.select(placeholder="Select radio",
                                   min_values=1,
                                   max_values=1,
                                   options=options)
                async def select_callback(self,
                                          interaction: discord.Interaction,
                                          select: ui.Select):
                    """
                        callback for the selection within the view.
                    """
                    await play_from_url(interaction, select.values[0])

            view = RadioView()
            await interaction.followup.send("Select a station:", view=view)
            return

        await play_from_url(interaction, source_url)

    @app_commands.command()
    @app_commands.guild_only()
    async def disconnect(self, interaction: discord.Interaction):
        """
        Disconnect bot from channel.
        """
        try:
            audio_stream = sources_on_guild.get(interaction.guild_id)
            await audio_stream.vc.disconnect()
            await interaction.response.send_message("Disconnected from channel"
                                                    )
        except discord.errors.ClientException as err:
            print(f"Error disconnecting from voice channel: {err}")
            await interaction.response.send_message(
                "Error disconnecting from channel")

    @app_commands.command()
    @app_commands.guild_only()
    async def volume(self, interaction: discord.Interaction, percentage: int):
        """
            Changes the Volume of the Audio for the current stream.
        """
        # grab the current audio stream.
        audio_stream = sources_on_guild.get(interaction.guild_id)

        # send message if not exists
        if not audio_stream:
            await interaction.response.send_message(
                "There is no audio stream in this guild.")
            return

        # set the volume
        audio_stream.transform.volume = percentage * 0.01

        await interaction.response.send_message(
            f"Set stream volume to {percentage}%")


async def setup(bot: commands.Bot):
    """
        Setup function for music module
    """
    opus.load_opus('libopus.so')
    if opus.is_loaded():
        await bot.add_cog(Music(bot))
    else:
        print("Wasn't able to load opus.")
