"A command group containing emote commands."
from random import choice
import hikari
import tanjun
from configloader import config, emote_links

component = tanjun.Component(name="emotes")

def generate_emoji_embed(action: str, myself: hikari.User, target: hikari.User = None) -> hikari.Embed:
    "Generates an emoji embed for an emote action."
    embed = hikari.Embed(color=0xff3300)

    if target:
        embed.description = config['emotes'][action]['with_target'].format(
            myself=myself.mention, target=target.mention
        )
    else:
        embed.description = config['emotes'][action]['alone'].format(
            myself=myself.mention
        )

    embed.set_image(choice(emote_links[action]))
    return embed

def create_emote_command(name: str, description: str) -> tanjun.SlashCommand:
    """A factory to create emote slash commands."""
    @tanjun.with_user_slash_option("target", "The user to direct the emote at.", default=None)
    @tanjun.as_slash_command(name, description)
    async def emote_command(ctx: tanjun.abc.Context, target: hikari.User | None):
        embed = generate_emoji_embed(name, ctx.author, target)
        await ctx.respond(embed=embed)

    return emote_command

# List of emotes to be generated
emote_list = {
    "hug": "Hug someone.",
    "cry": "For the sad times.",
    "smile": "For happy times.",
    "smug": "Surely something weird is happening.",
    "pat": "Nice pats.",
    "blush": "Do a blush.",
    "boop": "Boop someone.",
    "highfive": "Highfive someone.",
    "kiss": "Kiss someone.",
    "nom": "Nom someone.",
    "stare": "Staring...",
    "wave": "Waving...",
    "slap": "Slap someone.",
}

# Generate and add each emote command to the component
for name, description in emote_list.items():
    component.add_slash_command(create_emote_command(name, description))

@tanjun.as_loader
def load_component(client: tanjun.Client):
    "Loads the emote component."
    client.add_component(component.copy())