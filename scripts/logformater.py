"Log formatter used to format logs for discord channels."
from enum import Enum
from discord import Embed, Member

class AdminAction(Enum):
    "Administrative action a moderator, admin or owner would do."
    KICK    = "kick"
    BAN     = "ban"
    WARN    = "warn"

def format_moderation_event(target: Member, action: AdminAction, reason: str) -> Embed:
    "Format a reason and target"
    output = Embed()
    output.title = f"Moderation Action: >> {action.value} <<"
    output.add_field(name="Target", value=target.name)
    output.add_field(name="Reason", value=reason)
    return output
