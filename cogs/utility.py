"Core command group (commands ex. info, help)"
import discord
from discord.ext import commands, tasks
from api import bots_gg

TIMEFORMAT = "%m/%d/%Y, %H:%M:%S"

class HelpCommand(commands.MinimalHelpCommand):
    "Help Command for this bot, might add some custom methods."


class Utility(commands.Cog):
    "Basic functionalities of the bot, like information."

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        client.help_command = HelpCommand()
        client.help_command.cog = self

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        "Initialised tasks"
        # pylint: disable=no-member
        self.update_bot_statistics.start()

    async def cog_unload(self) -> None:
        "Cancels tasks"
        # pylint: disable=no-member
        self.update_bot_statistics.cancel()

    @commands.hybrid_command()
    async def info(self, ctx: commands.Context):
        "This command shows information about the bot."
        embed_message = discord.Embed()
        embed_message.title = self.client.user.name
        embed_message.add_field(
            name="Github Repo", value="https://github.com/ChinoCodeDemon/Aeses")
        embed_message.add_field(name="Framework", value="discord.py")
        embed_message.set_image(url=self.client.user.avatar.url)
        await ctx.send(embed=embed_message)

    @commands.hybrid_command()
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        "Give a better view on avatars"
        if not user:
            user = ctx.author
        embed = discord.Embed(title=user.name)
        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.guild_only()
    async def whois(self, ctx: commands.Context, member: discord.Member = None):
        "Gives you quick info about a member or yourself, useful for moderation."
        if not member:
            member = ctx.author
        embed = discord.Embed(title=f"Whois of {member.display_name}")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Username", value=member.name)
        embed.add_field(name="Roles", value=", ".join([r.mention for r in member.roles]))
        embed.add_field(name="Creation", value=member.created_at.strftime(TIMEFORMAT), inline=False)
        embed.add_field(name="Joined", value=member.joined_at.strftime(TIMEFORMAT), inline=False)
        await ctx.send(embed=embed)

    @tasks.loop(seconds=5)
    async def update_bot_statistics(self):
        "Updates statistics about the bot."
        if self.client.application_id:
            bots_gg.update_statistics(self.client.application_id, len(self.client.guilds))


async def setup(client: commands.Bot):
    "Setup function for 'info' cog"
    await client.add_cog(Utility(client))
