import json
import os

import discord
from discord import ButtonStyle
from discord.commands import Option
from discord.ui import InputText, Modal, View, Button, button
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
TOKEN = os.getenv('TOKEN')
GUILD = json.loads(os.getenv("GUILDS"))
bot = discord.Bot()


class ThreadModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="Thread Name", placeholder="Super Thread"))

    async def callback(self, interaction: discord.Interaction):
        thread = await interaction.channel.create_thread(name=self.children[0].value,
                                                         type=discord.ChannelType.public_thread)
        await interaction.response.send_message(f"Created thread `{self.children[0].value}`", ephemeral=True)
        await thread.add_user(interaction.user)
        await thread.remove_user(bot.user)


@bot.slash_command(name="setup", guild_ids=GUILD, description="Set a channel as a home for creating new threads")
async def setup(ctx, channel: Option(discord.TextChannel, "Select a channel to use for storing threads")):
    await ctx.defer(ephemeral=True)

    perms = discord.PermissionOverwrite()
    perms.send_messages = False
    perms.read_messages = True

    await channel.set_permissions(bot.user, send_messages=True, manage_webhooks=True)
    await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
    await channel.send("Click the button below to create a new thread", view=btn_createThread())
    await ctx.followup.send(f"Using `{str(channel)}` for threads")


@bot.slash_command(name="channel_to_thread", guild_ids=GUILD, description="Convert a channel to a thread with the "
                                                                          "option to remove the original channel")
async def channel_to_thread(ctx, channel: Option(discord.TextChannel, "Select a channel to turn into a thread"),
                            place: Option(discord.TextChannel, "Select a channel to create the thread in"),
                            name: Option(str, "Enter a name for the thread [Default: Channel Name]",
                                         required=False),
                            rejoin: Option(bool, "Add previous users from the channel to the thread automatically ("
                                                 "will cause a ping) [Default: False]", default=False),
                            remove: Option(bool, "Remove the original channel? (Probably can't be undone) "
                                                 "[Default: False]", default=False)):
    await ctx.defer(ephemeral=True)

    if not channel.can_send():
        await ctx.followup.send("Could not convert channel.\nIs the channel private?")
        return

    # Create webhook to emulate users posting in channels
    hook = await place.create_webhook(name="Channel to Thread [DELETE IF FOUND]", reason="Moving channel to thread")

    try:
        # Create a new thread
        thread = await place.create_thread(name=name or str(channel), type=discord.ChannelType.public_thread,
                                           reason=f"Moved channel: `{channel}` to a thread")

        # Create a list of messages from the selected channel
        hist = await channel.history(limit=None, oldest_first=True).flatten()

        for msg in hist:
            # Media that is marked as spoilers will need to be reuploaded due to bots not embedding spoilered URLs.
            # Any other media should be linked to just fine, working around the issue of Nitro uploads
            try:
                await hook.send(msg.content + '\n'.join([f.url for f in msg.attachments if not f.is_spoiler()]),
                                username=msg.author.display_name if type(msg.author) == discord.Member
                                else msg.author.name, avatar_url=msg.author.display_avatar.url,
                                embeds=msg.embeds, thread=thread,
                                files=[await f.to_file() for f in msg.attachments if f.is_spoiler()])
            # Pinned message notifications will be caught as messages with no content
            except discord.errors.HTTPException as err:
                print(type(err), err)

        if rejoin:
            for msg in hist:
                if msg.author not in thread.members and msg.author in ctx.guild.members:
                    await thread.add_user(msg.author)

        if remove:
            await channel.delete()

        await thread.remove_user(bot.user)
        await ctx.followup.send(f"Moved channel `{channel}` to a thread in `{place}`")
    except TypeError or discord.DiscordException as err:
        print(type(err), err)
        await ctx.followup.send(f"Could not move channel to thread\n{type(err)} {err}")
    finally:
        await hook.delete(reason=f"Moved channel `{channel}` to a thread in `{place}`. No longer needed")


# @bot.slash_command(name="remove_all_threads", guild_ids=GUILD, default_permission=False,
#                    description="Quickly remove all threads in the current channel")
# async def remove_all_threads(ctx):
#     await ctx.defer(ephemeral=True)
#
#     for t in ctx.channel.threads:
#         await t.delete()
#
#     await ctx.followup.send(f"Deleted all threads in channel `{ctx.channel}`")


@bot.event
async def on_ready():
    bot.add_view(btn_createThread())
    print(f"Logged in as {bot.user}")
    print(f"Creating invite link: https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}"
          f"&permissions=395942423568&scope=bot%20applications.commands")


class btn_createThread(View, discord.TextChannel):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Create new thread", style=ButtonStyle.green, emoji="➕", custom_id=f"button_newThread")
    async def button_callback(self, button, interaction):
        modal = ThreadModal(title="New Thread", custom_id=f"threadModal_newThread")
        await interaction.response.send_modal(modal)


bot.run(TOKEN)
