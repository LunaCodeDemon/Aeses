"This Cog lets server moderators change settings for the guild."
import hikari
import tanjun
from scripts import sqldata
from scripts.messagebuilders import generate_filtertype_listing

component = tanjun.Component(name="settings")

@component.with_slash_command
@tanjun.with_author_permission_check(hikari.Permissions.ADMINISTRATOR)
@tanjun.with_str_slash_option(
    "filter_type",
    "The type of filter to configure.",
    choices={
        "Emoji in Names": "emona",
        "Links": "links"
    },
    default=None
)
@tanjun.with_bool_slash_option("active", "Set the filter directly to active or inactive.", default=None)
@tanjun.as_slash_command("filterconf", "Configure content filters for this server.")
async def filterconf_command(
    ctx: tanjun.abc.Context,
    filter_type: str | None,
    active: bool | None
):
    """
    Set which filter type to enable.
    Calling it without a filter type lists all filters and their status.
    """
    if not filter_type:
        filterconfig = sqldata.get_filterconfig(ctx.guild_id)
        active_filters = [fi.filter_type for fi in filterconfig if fi.active]
        inactive_filters = [fi.filter_type for fi in filterconfig if not fi.active]

        all_known_filters = {ft for ft in sqldata.FilterType}
        configured_filters = set(active_filters) | set(inactive_filters)
        unconfigured_filters = all_known_filters - configured_filters
        inactive_filters.extend(unconfigured_filters)

        active_list = generate_filtertype_listing(active_filters) or "None"
        inactive_list = generate_filtertype_listing(inactive_filters) or "None"

        embed = hikari.Embed(title="Filters")
        embed.add_field(name="Active", value=active_list)
        embed.add_field(name="Inactive", value=inactive_list)
        await ctx.respond(embed=embed)
        return

    try:
        ftype = sqldata.FilterType(filter_type)
        if active is None:
            # Toggle logic
            current_config = sqldata.get_filterconfig(ctx.guild_id, ftype)
            current_active = current_config[0].active if current_config else False
            sqldata.insert_filterconfig(ctx.guild_id, ftype, not current_active)
        else:
            # Direct set logic
            sqldata.insert_filterconfig(ctx.guild_id, ftype, active)

        await ctx.respond("Filter settings updated.")
    except ValueError:
        await ctx.respond("Invalid filter type specified.")

@tanjun.as_loader
def load_component(client: tanjun.Client):
    "Loads the settings component."
    client.add_component(component.copy())