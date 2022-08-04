"Handles most sql actions"
import os
from sqlalchemy import create_engine, text

DB_FILENAME = "/data.db"
DEBUG = os.environ.get('DEBUG') or "false"
if DEBUG.lower() in ['true', 'yes', 't', '1']:
    DB_FILENAME = "/:memory:"

engine = create_engine(f"sqlite://{DB_FILENAME}", echo=True)

def create_table_logchannel():
    "Create a table for log channel"
    with engine.connect() as conn:
        conn.execute(
            text("CREATE TABLE IF NOT EXISTS logchannels"\
                "(channel_id unsigned long, "\
                "guild_id unsigned long);"))


def get_logchannel(guild_id: int) -> int | None:
    "Get the log channel of the guild."
    channel_id: int | None = None
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT channel_id FROM logchannels "\
                "WHERE guild_id == :guild_id"),
                [{"guild_id": guild_id}]
        ).first()
        channel_id = result[0] if result else None
    return channel_id

def update_logchannel(guild_id: int, channel_id: int) -> None:
    "Update channel_id for logchannel in guild."
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE logchannels"\
                "SET channel_id = :channel_id"\
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
            text("INSERT INTO logchannels (guild_id, channel_id)"\
                " VALUES (:guild_id, :channel_id)"),
            [{"guild_id": int(guild_id), "channel_id": int(channel_id)}])
