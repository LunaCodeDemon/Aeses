from typing import NamedTuple
from typing import Dict
import discord
from discord import app_commands
from discord import opus
from discord.ext import commands


class AudioStream(NamedTuple):
    """
        Structured tuple for audio streams
    """
    url: str
    source: discord.FFmpegPCMAudio
    transform: discord.PCMVolumeTransformer
    vc: discord.VoiceClient


sources_on_guild: Dict[int, AudioStream] = {}


class Music(commands.Cog):
    """
        Commands that interact with music.
    """
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.guild_only()
    @commands.bot_has_permissions(speak=True, connect=True)
    async def play(self, interaction: discord.Interaction, src: str):
        """
            Play music from a web stream. (Only Webradio Links for now)
        """
        voice_channel = interaction.user.voice.channel

        # grab the voice client that is available.
        try:
            voice_client = await voice_channel.connect(self_deaf=True)
        except (discord.GatewayNotFound, discord.ConnectionClosed):
            voice_client = sources_on_guild.get(interaction.guild_id).vc

        # creates an audio source object
        audio_source = discord.FFmpegPCMAudio(
            src,
            before_options='-reconnect 1 -reconnect_streamed 1 ' +
            '-reconnect_delay_max 5',
            options='-vn')

        # creates a volume transformer object
        audio_transform = discord.PCMVolumeTransformer(audio_source)

        # saves all objects for later use.
        sources_on_guild[interaction.guild_id] = AudioStream(
            url=src,
            source=audio_source,
            transform=audio_transform,
            vc=voice_client)

        # play audio from the audio_transform allowing for volume changes on the fly.
        voice_client.play(
            audio_transform,
            after=lambda e: sources_on_guild.pop(voice_channel.id))

        await interaction.response.send_message(f"Playing music from {src}")

    @app_commands.command()
    @app_commands.guild_only()
    async def disconnect(self, interaction: discord.Interaction):
        """
        Disconnect bot from channel.
        """
        try:
            audio_stream = sources_on_guild.get(interaction.guild_id)
            await audio_stream.vc.disconnect()
            await interaction.response.send_message("Disconnected from channel")
        except discord.errors.ClientException as err:
            print(f"Error disconnecting from voice channel: {err}")
            await interaction.response.send_message("Error disconnecting from channel")

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
            await interaction.response.send_message("There is no audio stream in this guild.")
            return

        # set the volume
        audio_stream.transform.volume = percentage * 0.01

        await interaction.response.send_message(f"Set stream volume to {percentage}%")


async def setup(bot: commands.Bot):
    """
        Setup function for music module
    """
    opus.load_opus('libopus.so')
    if opus.is_loaded():
        await bot.add_cog(Music(bot))
    else:
        print("Wasn't able to load opus.")
