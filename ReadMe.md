# Activity Enhancing Spam Erasing System
Aeses is focused on enhancing the Activity of a community and erasing possible spam.
I will try to make Aeses powerful enough to be a standalone tool.

## Dependencies
1. [python](https://www.python.org/)
2. [discord.py](https://discordpy.readthedocs.io/en/stable/intro.html)
3. emoji `pip install -U emoji`

### Fast install dependencies
To install the dependencies, install [python](https://www.python.org/) and then run this command inside the project folder.
```
pip install -U -r requirements.txt
```

## Setup the bot.
1. Install [dependencies](#dependencies)
2. Get a discord token on the official [developer page](https://discord.com/developers/)
3. Make a start script (.sh or .bat) with this content.
```
DISCORD_TOKEN=<your token> python app.py
```

### Pro-Tip
Using a process manager you can make sure your bot stays active even if your server/computer restarts.
Simply use one like [pm2](https://pm2.keymetrics.io/) or [forever](https://github.com/foreversd/forever)


## Commands
It is recommended to use the `help` command to get infos on how to use commands.
| Command       | Description               |
|---            | ---                       |
| `!help`       | Gives help for commands   |
| `!ban`        | Bans a guild member.      |
| `!kick`       | Kicks a guild member.     |
| `!logchannel` | Set log channel.          |

---

## Goal of this project
This will also be a bit of a to-do list for me.
The aspects of moderation and spam protection are most important to me, but i am also open for suggestions.

### Moderation Goals
- Fully integrated spam protection
- Strike command
- Logging for moderative actions

### Activity Enhancing Goals
- Automatic messages in dead main channels.
- Daily messages (questions, steamdb sales, statements or images)
- Giveaway functionality (picking people)

### Configuration Goals
- Messages for moderation commands should be fully configurable.

