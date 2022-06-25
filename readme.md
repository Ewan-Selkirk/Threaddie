# Threaddie - A Discord bot for transferring channels to threads
________________________________________________________________
## Commands
| Command              | Options                                                                      | Description                                                                                                                                                                                                                                                                            |
|----------------------|------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| /setup               | `channel`: TextChannel                                                       | Setup a channel (`channel`) as read-only; where users can create new threads.                                                                                                                                                                                                          |
| /channel_to_thread   | `channel`: TextChannel, `place`: TextChannel, `rejoin`: bool, `remove`: bool | Transfer the content of a channel (`channel`) to a thread in the channel `place`. `rejoin` determines whether users who've interacted wtih the original channel should be automatically added to the thread (causes a ping). `remove` will delete the original channel if set to true. |
| /remove_all_threads* | N/A                                                                          | Remove all threads in the current channel                                                                                                                                                                                                                                              |

*Currently unavailable due to permission changes
## Installation and Running
### Without virtualenv
- Skip to [Continuation](#continuation)

### With virtualenv
- Create a virtual environment with `python -m venv ./venv`
- Activate the envirnment with:
  - `source venv/bin/activate` on Unix systems
  - `.\venv\Scripts\Activate.ps1` on Windows (Powershell)

### Continuation
- Install the requirements with `pip install -r requirements.txt`
- Create a [Discord application](https://discord.com/developers/applications) and enable bot functionality
- Create an `.env` file in the same folder at `bot.py` and place your bot token as `TOKEN=your-token-here`
- Enable developer mode in Discord to be able to copy IDs (Settings -> Advanced -> Developer Mode)
- Set the guild ID of the server(s) inside the `.env` file as `GUILDS='["ID_HERE"]'` (quotation marks required)
- Set the client ID found in the OAuth2 page as `CLIENT_ID=ID`
- Run `bot.py`
- Click the generated link to invite the bot to your server

## Acknowledgements
This project wouldn't be possible without the work of [discord.py](https://github.com/Rapptz/discord.py) and its continuation, [pycord](https://github.com/Pycord-Development/pycord/)
