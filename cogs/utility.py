"Core command group (commands ex. info, help)"
import discord
from discord.ext import commands


class HelpCommand(commands.MinimalHelpCommand):
    "Help Command for this bot, might add some custom methods."


class Utility(commands.Cog):
    "Basic functionalities of the bot, like information."

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        client.help_command = HelpCommand()
        client.help_command.cog = self

    @commands.command()
    async def info(self, ctx: commands.Context):
        "This command shows information about the bot."
        embed_message = discord.Embed()
        embed_message.title = self.client.user.name
        embed_message.add_field(
            name="Github Repo", value="https://github.com/ChinoCodeDemon/Aeses")
        embed_message.add_field(name="Framework", value="discord.py")
        embed_message.set_image(url=self.client.user.avatar_url)
        await ctx.send(embed=embed_message)


async def setup(client: commands.Bot):
    "Setup function for 'info' cog"
    await client.add_cog(Utility(client))
