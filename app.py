"Entrypoint of project"

import os
from bot import client

client.run(os.environ.get('DISCORD_TOKEN'))
