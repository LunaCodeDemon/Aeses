"Handles most sql actions"
from dataclasses import dataclass
from enum import Enum
import os
from typing import Optional, List
from sqlalchemy import create_engine, text

from scripts.conversion import str2bool

DB_ENGINE = os.environ.get("DATABASE_ENGINE") or "sqlite"
DB_URL = os.environ.get("DATABASE_URL") or "/data.db"
DEBUG = str2bool(os.environ.get("DEBUG"))
if str2bool(DEBUG):
    DB_URL = "/:memory:"
    DB_ENGINE = "sqlite"

engine = create_engine(f"{DB_ENGINE}://{DB_URL}", echo=DEBUG)


class FilterType(Enum):
    "Enum for filter types"
    EMOJI_NAME = "emona"
    LINK = "links"


@dataclass
class FilterConfig:
    "Filter configurations"
    guild_id: int
    filter_type: FilterType
    active: bool

def create_table_logchannel():
    "Create a table for log channel"
    with engine.connect() as conn:
        conn.execute(
            text("CREATE TABLE IF NOT EXISTS logchannels"
                 "(channel_id bigint, "
                 "guild_id bigint);"))


def get_logchannel(guild_id: int) -> Optional[int]:
    "Get the log channel of the guild."
    channel_id: Optional[int] = None
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT channel_id FROM logchannels "
                 "WHERE guild_id == :guild_id"),
            [{"guild_id": guild_id}]
        ).first()
        channel_id = result[0] if result else None
    return channel_id


def update_logchannel(guild_id: int, channel_id: int) -> None:
    "Update channel_id for logchannel in guild."
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE logchannels"
                 "SET channel_id = :channel_id"
                 "WHERE guild_id = :guild_id"),
            [{"guild_id": guild_id, "channel_id": channel_id}]
        )


def insert_logchannel(guild_id: int, channel_id: int) -> None:
    "Insert logchannel into database"

    # Guard to prevent having multiple log channels.
    if get_logchannel(guild_id):
        update_logchannel(guild_id, channel_id)
        return

    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO logchannels (guild_id, channel_id)"
                 " VALUES (:guild_id, :channel_id)"),
            [{"guild_id": guild_id, "channel_id": channel_id}])


def create_table_filterconfig():
    "Creates a table for guild filter."
    with engine.connect() as conn:
        conn.execute(
            text(
            "CREATE TABLE IF NOT EXISTS filterconfig("
            "guild_id bigint, "
            "filter_type VARCHAR(8), "
            "active boolean"
            ");"
            )
        )


def get_filterconfig(guild_id: int, filter_type: FilterType = None) -> Optional[List[FilterConfig]]:
    "Get filter config for guild, can be multiple."
    query = (
        "SELECT * FROM filterconfig "
        "WHERE guild_id = :guild_id "
    )
    params = {
        "guild_id": guild_id
    }
    if filter_type:
        query += "AND filter_type = :filter_type"
        params.update({"filter_type": filter_type.value})
    with engine.connect() as conn:
        result = conn.execute(
            text(query),
            params
        ).all()
        return result and [
            FilterConfig(
                guild_id=filterconfig[0],
                filter_type=FilterType(filterconfig[1]),
                active=bool(filterconfig[2])
            )
            for filterconfig in result
        ]


def update_filterconfig(guild_id: int, filter_type: FilterType, active: bool):
    "Update filterconfig status"
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE filterconfig "
            "SET active = :active "
            "WHERE guild_id = :guild_id "
            "AND filter_type = :filter_type;"),
            {"filter_type": filter_type.value,
                "guild_id": guild_id, "active": active}
        )


def insert_filterconfig(guild_id: int, filter_type: FilterType, active: bool):
    "Insert filter configuration."
    if get_filterconfig(guild_id, filter_type) in [[], None]:
        update_filterconfig(guild_id, filter_type, active)
        return

    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO filterconfig (guild_id, filter_type, active) "
            "VALUES (:guild_id, :filter_type, :active)"),
            {"guild_id": guild_id, "filter_type": filter_type.value, "active": active}
        )


create_table_filterconfig()
# create_table_logchannel()
