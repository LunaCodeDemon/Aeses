"Entrypoint of project"

import logging
import os
from bot import client

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

def main():
    "Startpoint of the script."
    if not DISCORD_TOKEN:
        logging.error("Unable to login into Discord, please set DISCORD_TOKEN.")
        return
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
