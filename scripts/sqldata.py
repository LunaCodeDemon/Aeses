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


class LogType(Enum):
    "Types for logging."
    WELCOME = "welcome"
    MODERATION = "moderation"


@dataclass
class LoggingChannel:
    "Log channel info"
    guild_id: int
    channel_id: int
    logtype: LogType


def create_table_logchannel():
    "Create a table for log channel"
    with engine.connect() as conn:
        conn.execute(
            text("""CREATE TABLE IF NOT EXISTS logchannels
                 (channel_id bigint, 
                 guild_id bigint,
                 logtype varchar(15));"""))


def get_logchannel(guild_id: int, logtype: LogType = None) -> Optional[List[LoggingChannel]]:
    "Get the log channel of the guild."
    query = """SELECT channel_id, logtype FROM logchannels 
                 WHERE guild_id = :guild_id"""
    ltype = None
    if logtype:
        query += "\nAND logtype = :logtype"
        ltype = logtype.value
    channel_id: Optional[int] = None
    with engine.connect() as conn:
        result = conn.execute(
            text(query),
            [{"guild_id": guild_id, "logtype": ltype}]
        )
        channel_id = None if not result else [LoggingChannel(
            guild_id,
            logchannel[0],
            LogType(logchannel[1])
        ) for logchannel in result
        ]
    return channel_id


def update_logchannel(guild_id: int, channel_id: int, logtype: LogType) -> None:
    "Update channel_id for logchannel in guild."
    with engine.connect() as conn:
        conn.execute(
            text("""UPDATE logchannels
                 SET channel_id = :channel_id
                 WHERE guild_id = :guild_id
                 AND logtype = :logtype;"""),
            [{"guild_id": guild_id, "channel_id": channel_id, "logtype": logtype.value}]
        )


def insert_logchannel(guild_id: int, channel_id: int, logtype: LogType) -> None:
    "Insert logchannel into database"

    # Guard to prevent having multiple log channels.
    if get_logchannel(guild_id, logtype):
        update_logchannel(guild_id, channel_id, logtype)
        return

    with engine.connect() as conn:
        conn.execute(
            text("""INSERT INTO logchannels (guild_id, channel_id, logtype)
                  VALUES (:guild_id, :channel_id, :logtype)"""),
            [{"guild_id": guild_id, "channel_id": channel_id, "logtype": logtype.value}])


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
    if not get_filterconfig(guild_id, filter_type) in [[], None]:
        update_filterconfig(guild_id, filter_type, active)
        return

    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO filterconfig (guild_id, filter_type, active) "
                 "VALUES (:guild_id, :filter_type, :active)"),
            {"guild_id": guild_id, "filter_type": filter_type.value, "active": active}
        )


create_table_filterconfig()
create_table_logchannel()
