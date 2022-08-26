"Entrypoint of project"

import logging
import os
import asyncio
from dotenv import load_dotenv
from bot import client

load_dotenv()

discord_token = os.environ.get('DISCORD_TOKEN')


def main():
    "Startpoint of the script."
    if not discord_token:
        logging.error(
            "Unable to login into Discord, please set DISCORD_TOKEN.")
        return

    extension_folder = 'cogs'
    asyncio.run(client.load_modules_from_folder(extension_folder))
    client.run(discord_token)


if __name__ == "__main__":
    main()
