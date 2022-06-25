import json
import os

import discord
from discord.commands import Option
from discord.ui import InputText, Modal, View
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
        await thread.remove_user(bot.user)


@bot.slash_command(name="setup", guild_ids=GUILD, description="Set a channel as a home for creating new threads")
async def setup(ctx, channel: Option(discord.TextChannel, "Select a channel to use for storing threads")):
    await ctx.defer(ephemeral=True)

    perms = discord.PermissionOverwrite()
    perms.send_messages = False
    perms.read_messages = True

    await channel.set_permissions(bot.user, send_messages=True, manage_webhooks=True)
    await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
    await channel.send("Click the button below to create a new thread", view=btn_view())
    await ctx.followup.send(f"Using `{str(channel)}` for threads")


@bot.slash_command(name="channel_to_thread", guild_ids=GUILD, description="Convert a channel to a thread with the "
                                                                            "option to remove the original channel")
async def channel_to_thread(ctx, channel: Option(discord.TextChannel, "Select a channel to turn into a thread"),
                            place: Option(discord.TextChannel, "Select a channel to create the thread in"),
                            rejoin: Option(bool, "Add previous users from the channel to the thread automatically ("
                                                 "will cause a ping)"),
                            remove: Option(bool, "Remove the original channel? (Probably can't be undone)")):
    await ctx.defer(ephemeral=True)

    if not channel.can_send():
        await ctx.followup.send("Could not convert channel. Is the channel private?")
        return

    try:
        # Create webhook to emulate users posting in channels
        hook = await place.create_webhook(name="Channel to Thread [DELETE IF FOUND]", reason="Moving channel to thread")

        # Create a new thread
        thread = await place.create_thread(name=str(channel), type=discord.ChannelType.public_thread,
                                           reason=f"Moved channel: `{channel}` to a thread")

        # Create a list of messages from the selected channel
        hist = await channel.history(limit=None, oldest_first=True).flatten()

        for msg in hist:
            await hook.send(msg.content or ' ', username=msg.author.display_name,
                            avatar_url=msg.author.display_avatar.url, embeds=msg.embeds, thread=thread,
                            files=[await f.to_file() for f in msg.attachments])

        if rejoin:
            for msg in hist:
                if msg.author not in thread.members:
                    await thread.add_user(msg.author)

        if remove:
            await channel.delete()

        await thread.remove_user(bot.user)
        await hook.delete(reason=f"Moved channel `{channel}` to a thread in `{place}`. No longer needed")
        await ctx.followup.send(f"Moved channel `{channel}` to a thread in `{place}`")
    except TypeError or discord.DiscordException as err:
        print(type(err), err)
        await ctx.followup.send("Could not move channel to thread")


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
    bot.add_view(btn_view())
    print(f"Logged in as {bot.user}")
    print(f"Creating invite link: https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}"
          f"&permissions=395942423568&scope=bot%20applications.commands")


class btn_view(View, discord.TextChannel):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create new thread",
                       style=discord.ButtonStyle.green, emoji="➕",
                       custom_id=f"button_newThread")
    async def button_callback(self, button, interaction):
        modal = ThreadModal(title="New Thread", custom_id=f"threadModal_newThread")
        await interaction.response.send_modal(modal)


bot.run(TOKEN)
