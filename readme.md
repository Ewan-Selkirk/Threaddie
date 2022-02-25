# Threaddie - A Discord bot for transferring channels to threads

## Commands
| Command | Options | Description |
| --- | --- | --- |
| /setup | `channel`: TextChannel | Setup a channel (`channel`) as read-only; where users can create new threads. |
| /channel_to_thread | `channel`: TextChannel, `place`: TextChannel, `rejoin`: bool, `remove`: bool | Transfer the content of a channel (`channel`) to a thread in the channel `place`. `rejoin` determines whether users who've interacted wtih the original channel should be automatically added to the thread (causes a ping). `remove` will delete the original channel if set to true.|
| /remove_all_threads | N/A | Remove all threads in the current channel |

## Installation and Running
- Create a [Discord application](https://discord.com/developers/applications) and enable bot functionality
- Create an `.env` file in the same folder at `bot.py` and place your bot token as `TOKEN={your-token-here}`
- Enable developer mode in Discord to be able to copy IDs (Settings -> Advanced -> Developer Mode)
- Set the guild ID of the server inside the `.env` file as `GUILD={guild-id}`
- Invite the bot to your server using the OAuth2 URL generator: 
  - `https://discord.com/api/oauth2/authorize?client_id={YOUR-TOKEN-HERE}&permissions=395942423568&scope=bot%20applications.commands`
- Run `bot.py`