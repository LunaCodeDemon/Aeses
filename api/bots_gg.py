"Module that will interact with bots.gg"
import os
import httpx

BOTS_GG_TOKEN = os.environ("BOTS_GG_TOKEN")
BOTS_GG_URL = "https://discord.bots.gg/api/v1"

def update_statistics(client_id: str, guild_count: int):
    "updates statistics in bots.gg"
    if not BOTS_GG_TOKEN:
        return # should be ignored without token
    httpx.post(BOTS_GG_URL + f"/bots/{client_id}/stats",
        auth=BOTS_GG_TOKEN,
        json={"guildCount": guild_count})
