"Entrypoint of project"

import logging
import os
import asyncio
from dotenv import load_dotenv
from bot import client

load_dotenv()

discord_token = os.environ.get('DISCORD_TOKEN')


async def main():
    "Startpoint of the script."
    if not discord_token:
        logging.error(
            "Unable to login into Discord, please set DISCORD_TOKEN.")
        return

    extension_folder = 'cogs'
    await client.load_modules_from_folder(extension_folder)
    async with client:
        await client.start(discord_token)


if __name__ == "__main__":
    asyncio.run(main())
