"Module that will interact with bots.gg"
import logging
import os
import httpx

BOTS_GG_TOKEN = os.environ.get("BOTS_GG_TOKEN")
BOTS_GG_URL = "https://discord.bots.gg/api/v1"

def update_statistics(client_id: str, guild_count: int):
    "updates statistics in bots.gg"
    if not BOTS_GG_TOKEN:
        return # should be ignored without token
    response = httpx.post(BOTS_GG_URL + f"/bots/{client_id}/stats",
        json={"guildCount": guild_count},
        headers={"Authorization": BOTS_GG_TOKEN})
    logging.info(response.content)
