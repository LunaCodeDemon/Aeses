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


class MusicImplementation(commands.Cog):
    """
        Commands that interact with music.
    """
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.guild_only()
    async def play(self, interaction: discord.Interaction, src: str):
        """
            Play music from a web stream.
        """
        voice_channel = interaction.user.voice.channel

        try:
            voice_client = await voice_channel.connect()
        except (discord.GatewayNotFound, discord.ConnectionClosed):
            voice_client = sources_on_guild.get(interaction.guild_id).vc

        audio_source = discord.FFmpegPCMAudio(
            src,
            before_options='-reconnect 1 -reconnect_streamed 1 ' +
            '-reconnect_delay_max 5',
            options='-vn')
        audio_transform = discord.PCMVolumeTransformer(audio_source)

        voice_client.play(
            audio_source,
            after=lambda e: sources_on_guild.pop(voice_channel.id))
        sources_on_guild[voice_channel.id] = AudioStream(
            url=src,
            source=audio_source,
            transform=audio_transform,
            vc=voice_client)
        interaction.response.send_message(f"Playing music from {src}")

    @app_commands.command()
    @app_commands.guild_only()
    async def disconnect(self, interaction: discord.Interaction):
        """
            Disconnect bot from channel.
        """
        voice_client = sources_on_guild.pop(interaction.guild_id).vc
        voice_client.stop()
        voice_client.disconnect()
        interaction.response.send_message("Disconnected from channel")


def setup(bot: commands.Bot):
    """
        Setup function for music module
    """
    if opus.is_loaded():
        bot.add_cog(MusicImplementation(bot))
