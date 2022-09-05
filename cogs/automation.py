"""
Cog module for automations.
This includes reminder and dailies
"""
import discord
from discord.ext import commands, tasks


class Automation(commands.Cog):
    "Cog for automations like reminder and dailies"

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        "This gets triggered if the bot is ready"
        # pylint: disable=no-member
        await self.reminder_update.start()
        await self.daily_update.start()

    async def cog_unload(self) -> None:
        # pylint: disable=no-member
        await self.reminder_update.stop()
        await self.daily_update.stop()
        await super().cog_unload()

    # @tasks.loop(seconds=1)
    # async def reminder_update(self):
    #     pass  # TODO: implement reminder

    @tasks.loop(hours=24)
    async def daily_update(self):
        pass  # TODO: implement daily


async def setup(client: commands.Bot):
    "The usual setup function."
    client.add_cog(Automation(client))
