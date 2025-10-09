"Core command group (commands ex. info, help)"
import hikari
import tanjun
from api import bots_gg
from tanjun.schedules import every

TIMEFORMAT = "%m/%d/%Y, %H:%M:%S"

component = tanjun.Component()

async def generate_whois_embed(member: hikari.Member) -> hikari.Embed:
    "Generate a full whois embed for the given member"
    embed = hikari.Embed(title=f"Whois of {member.display_name}", color=member.accent_color)
    embed.set_thumbnail(member.display_avatar_url)

    embed.add_field(name="Username", value=str(member))

    roles = ", ".join(r.mention for r in member.get_roles())
    if roles:
        embed.add_field(name="Roles", value=roles)

    embed.add_field(name="Creation", value=member.created_at.strftime(TIMEFORMAT), inline=False)
    if member.joined_at:
        embed.add_field(name="Joined", value=member.joined_at.strftime(TIMEFORMAT), inline=False)

    return embed

async def generate_avatar_embed(user: hikari.User) -> hikari.Embed:
    "Generate an embed containing the avatar of the user"
    embed = hikari.Embed(title=user.username, color=user.accent_color)
    embed.set_image(user.avatar_url)
    return embed

@component.with_slash_command
@tanjun.as_slash_command("info", "This command shows information about the bot.")
async def info_command(ctx: tanjun.abc.Context, bot: hikari.GatewayBot = tanjun.inject()):
    "This command shows information about the bot."
    me = bot.get_me()
    embed = hikari.Embed(title=me.username)
    embed.add_field(name="Github Repo", value="https://github.com/ChinoCodeDemon/Aeses")
    embed.add_field(name="Support Server", value="https://discord.gg/StgE5Z4bFB")
    embed.add_field(name="Framework", value="Hikari + Tanjun")
    embed.set_image(me.avatar_url)
    await ctx.respond(embed=embed)

@component.with_slash_command
@tanjun.as_slash_command("invite", "Sends back an invite link for the bot.")
async def invite_command(ctx: tanjun.abc.Context, bot: hikari.GatewayBot = tanjun.inject()):
    "Sends back an invite link for the bot."
    app = bot.application
    link = f"https://discord.com/api/oauth2/authorize?client_id={app.id}&permissions=2281712656&scope=bot%20applications.commands"
    embed = hikari.Embed(
        title="Invite",
        description=f"You can use this link to invite the bot into your server:\n{link}"
    )
    await ctx.respond(embed=embed)

@component.with_slash_command
@tanjun.with_user_slash_option("user", "The user to get the avatar of.", default=None)
@tanjun.as_slash_command("avatar", "Give a better view on avatars")
async def avatar_command(ctx: tanjun.abc.Context, user: hikari.User | None):
    "Give a better view on avatars"
    target_user = user or ctx.author
    embed = await generate_avatar_embed(target_user)
    await ctx.respond(embed=embed)

@component.with_slash_command
@tanjun.with_member_slash_option("member", "The member to get info about.", default=None)
@tanjun.as_slash_command("whois", "Gives you quick info about a member or yourself.")
async def whois_command(ctx: tanjun.abc.Context, member: hikari.Member | None):
    "Gives you quick info about a member or yourself."
    target_member = member or ctx.member
    if not target_member:
        await ctx.respond("Could not find member.")
        return

    embed = await generate_whois_embed(target_member)
    await ctx.respond(embed=embed)

@component.with_user_menu
@tanjun.as_user_menu("Whois", dm_enabled=False)
async def whois_menu(ctx: tanjun.abc.MenuContext, member: hikari.Member):
    "Get a whois over contex menu"
    embed = await generate_whois_embed(member)
    await ctx.respond(embed=embed)

@component.with_user_menu
@tanjun.as_user_menu("Avatar")
async def avatar_menu(ctx: tanjun.abc.MenuContext, user: hikari.User):
    "Get an avatar over contex menu"
    embed = await generate_avatar_embed(user)
    await ctx.respond(embed=embed)

@component.with_schedule(every(minutes=30))
async def update_bot_statistics(bot: hikari.GatewayBot = tanjun.inject()):
    "Updates statistics about the bot."
    if bot.application:
        bots_gg.update_statistics(bot.application.id, len(bot.cache.get_guilds_view()))

@tanjun.as_loader
def load_component(client: tanjun.Client):
    "Loads the component"
    client.add_component(component.copy())