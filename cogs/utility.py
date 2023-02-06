"Core command group (commands ex. info, help)"
import discord
from discord import app_commands
from discord.ext import commands, tasks
from api import bots_gg
from bot import AesesBot

TIMEFORMAT = "%m/%d/%Y, %H:%M:%S"


async def generate_whois_embed(member: discord.Member):
    "Generate a full whois embed for the given member"

    embed = discord.Embed(title=f"Whois of {member.display_name}")
    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="Username", value=member.name)
    embed.add_field(name="Roles",
                    value=", ".join([r.mention for r in member.roles]))

    embed.add_field(name="Creation",
                    value=member.created_at.strftime(TIMEFORMAT),
                    inline=False)
    embed.add_field(name="Joined",
                    value=member.joined_at.strftime(TIMEFORMAT),
                    inline=False)

    return embed


async def generate_avatar_embed(user: discord.User):
    "Generate an embed containing the avatar of the user"

    embed = discord.Embed(title=user.name)
    embed.set_image(url=user.avatar.url)

    return embed


@app_commands.context_menu(name="Whois")
async def menu_whois(interaction: discord.Interaction, member: discord.Member):
    "Get a whois over contex menu"

    embed = await generate_whois_embed(member)
    interaction.response.send_message(embed=embed)


@app_commands.context_menu(name="Avatar")
async def menu_avatar(interaction: discord.Interaction,
                      member: discord.Member):
    "Get a whois over contex menu"

    embed = await generate_whois_embed(member)
    interaction.response.send_message(embed=embed)


class Utility(commands.Cog):
    "Basic functionalities of the bot, like information."

    def __init__(self, client: AesesBot) -> None:
        self.client = client
        # client.help_command = HelpCommand()
        # client.help_command.cog = self
        client.add_context_menus([menu_whois, menu_avatar])

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        "Initialised tasks"
        # pylint: disable=no-member
        self.update_bot_statistics.start()

    async def cog_unload(self) -> None:
        "Cancels tasks"
        # pylint: disable=no-member
        self.update_bot_statistics.cancel()

    @app_commands.command()
    async def info(self, inter: discord.Interaction):
        "This command shows information about the bot."
        embed_message = discord.Embed()

        embed_message.title = self.client.user.name

        embed_message.add_field(
            name="Github Repo",
            value="https://github.com/ChinoCodeDemon/Aeses")
        embed_message.add_field(name="Support Server",
                                value="https://discord.gg/StgE5Z4bFB")

        embed_message.add_field(name="Framework", value="discord.py")

        embed_message.set_image(url=self.client.user.avatar.url)

        await inter.response.send_message(embed=embed_message)

    @app_commands.command()
    async def invite(self, inter: discord.Interaction):
        "Sends back an invite link for the bot."
        # This line is long because of the url that only gets used at that spot.
        # pylint: disable=line-too-long
        link = f"https://discord.com/api/oauth2/authorize?client_id={self.client.application_id}&permissions=2281712656&scope=bot"

        embed = discord.Embed(
            title="Invite",
            # pylint: disable=line-too-long
            description=
            f"You can use this link this link to invite the bot into your server:\n{link}"
        )

        await inter.response.send_message(embed=embed)

    @app_commands.command()
    async def avatar(self,
                     inter: discord.Interaction,
                     user: discord.User = None):
        "Give a better view on avatars"
        # assume the target to be the author if not given.
        if not user:
            user = inter.user

        embed = await generate_avatar_embed(user)
        await inter.response.send_message(embed=embed)

    @app_commands.command()
    @commands.guild_only()
    async def whois(self,
                    inter: discord.Interaction,
                    member: discord.Member = None):
        "Gives you quick info about a member or yourself, useful for moderation."
        # assume the target to be the author if not given.
        if not member:
            member = inter.user

        embed = await generate_whois_embed(member)
        await inter.response.send_message(embed=embed)

    @tasks.loop(seconds=5)
    async def update_bot_statistics(self):
        "Updates statistics about the bot."
        if self.client.application_id:
            bots_gg.update_statistics(self.client.application_id,
                                      len(self.client.guilds))


async def setup(client: commands.Bot):
    "Setup function for 'info' cog"
    await client.add_cog(Utility(client))
