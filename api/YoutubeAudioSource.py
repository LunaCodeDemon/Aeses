"""
    A tiny implementation of a youtube music source
"""

import asyncio
import discord
import youtube_dl

from exceptions import UnableToExtractInfo, UnsupportedFeature

ytdl_format_options = {
    'audioquality': 5,
    'format': 'bestaudio',
    'outtmpl': '{}',
    'restrictfilenames': True,
    'flatplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    "extractaudio": True,
    "audioformat": "opus",
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

class YoutubeAudioSource(discord.PCMVolumeTransformer):
    def __init__(self, original: discord.FFmpegPCMAudio, *, volume: float = 1):
        super().__init__(original, volume)

    @classmethod
    async def from_url(cls, url: str, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        ytdl = youtube_dl.YoutubeDL()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if not data:
            raise UnableToExtractInfo("Cannot get data from youtbe.")
        
        if 'entries' in data:
            # TODO playlist capabilities
            raise UnsupportedFeature("Playlists are currently not supported.")

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, options='-vn'))
