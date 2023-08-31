#cog by @maxy_dev (maxy#2866)
import asyncio
import disnake as discord
import random
import os, sys
import datetime, time
from enum import Enum
from disnake.ext import commands
from utils import db, datasaver, defaultset, dividers

botver = "4.8.1"
pyver = ".".join(str(i) for i in list(sys.version_info)[0:3])
dnver = ".".join(str(i) for i in list(discord.version_info)[0:3])

settingkeys = {"msg_ignore_unknown": ("Ignore unknown message links", "Self explanatory"),
               "no_embed_on_mention": ("No embed on mention", "No 'Hello!' embed when you mention the bot"),
               "msg_ignore_all": ("Ignore messages", "Ignores all of your links and messages"),
               "anon": ("Anonymous", "Your username and pfp wont be displayed in embedded messages\n> Use `/settings anon` to set it up")}

class Anon(str, Enum):
  All_Servers = True
  Off = False
  Servers_you_arent_in = "servers you arent in"

class Setting(str, Enum):
  msg_ignore_unknown = "msg_ignore_unknown"
  no_embed_on_mention = "no_embed_on_mention"
  msg_ignore_all = "msg_ignore_all"

escapesetkeys = ["anon"]

async def suggest_setting(inter, input):
  if str(inter.author.id) not in db["settings"]:
    db["settings"][str(inter.author.id)] = defaultset.copy()
  else:
    for i in defaultset.keys():
      if i not in db["settings"][str(inter.author.id)]:
        db["settings"][str(inter.author.id)][i] = False
  return [setting for setting in list(db['settings'][str(inter.author.id)].keys()) if input.lower() in setting.lower() and setting.lower() not in escapesetkeys][0:24]

def change_setting(inter, setting: str, value: str | bool):
  if isinstance(value, str):
    value = True if value.lower() == "true" else False if value.lower() == "false" else value
  if value == db["settings"][str(inter.author.id)][setting]:
    e = discord.Embed(title = "Error", description = "This setting is already set to this value", color = random.randint(0, 16777215))
    return e
  db["settings"][str(inter.author.id)][setting] = value
  e = discord.Embed(title = "Success", description = "Setting updated!", color = random.randint(0, 16777215))
  return e

class Utility(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.message_command(name = "Delete Message")
  async def delete(self, inter: discord.Interaction, msg: discord.Message):
    if str(inter.author.id) not in datasaver:
      datasaver[str(inter.author.id)] = []
    if "Delete message" not in db["analytics"]["day"]:
      db["analytics"]["day"]["Delete message"] = 0
    if str(msg.id) not in datasaver[str(inter.author.id)]:
      e = discord.Embed(title = "Error", description = "You can not delete this message\nThere is a few reasons for that:\n\n1. User is not a webhook or a bot\n2. The message wasn't sent by a webhook\n3. Its not your webhook's message", color = random.randint(0, 16777215))
      await inter.response.send_message(embed = e, ephemeral = True)
      db["analytics"]["day"]["errored"] += 1
      return
    datasaver[str(inter.author.id)].discard(str(msg.id))
    await msg.delete()
    e = discord.Embed(title = "Success", description = "Message deleted!", color = random.randint(0, 16777215))
    await inter.response.send_message(embed = e, ephemeral = True)
    db["analytics"]["day"]["Delete message"] += 1

  @commands.slash_command()
  async def delete_msg(self, inter, msgid: discord.Message):
    '''
    Delete an embed with Message ID

    Parameters
    ----------
    msgid: Message ID
    '''
    if str(inter.author.id) not in datasaver:
      datasaver[str(inter.author.id)] = []
    if "Delete message" not in db["analytics"]["day"]:
      db["analytics"]["day"]["Delete message"] = 0
    msg = await inter.bot.get_channel(msgid.channel.id).fetch_message(msgid.id)
    if str(msg.id) not in datasaver[str(inter.author.id)]:
      e = discord.Embed(title = "Error", description = "You can not delete this message\nThere is a few reasons for that:\n\n1. User is not a webhook or a bot\n2. The message wasn't sent by a webhook/bot\n3. Its not your webhook/bot's message", color = random.randint(0, 16777215))
      await inter.send(embed = e, ephemeral = True)
      db["analytics"]["day"]["errored"] += 1
      return
    datasaver[str(inter.author.id)].discard(str(msg.id))
    await msg.delete()
    e = discord.Embed(title = "Success", description = "Message deleted!", color = random.randint(0, 16777215))
    await inter.send(embed = e, ephemeral = True)
    db["analytics"]["day"]["Delete message"] += 1

  #TODO: add edit button and command

  @commands.slash_command()
  async def settings(self, inter):
    if str(inter.author.id) not in db["settings"]:
      db["settings"][str(inter.author.id)] = defaultset.copy()
    else:
      for i in defaultset.keys():
        if i not in db["settings"][str(inter.author.id)]:
          db["settings"][str(inter.author.id)][i] = False

  @settings.sub_command()
  async def anon(self, inter, value: Anon):
    '''
    Change your anonymous settings

    Parameters
    ----------
    value: All servers, Off, Servers you arent in
    '''
    await inter.response.defer(ephemeral = True)
    await inter.send(embed = change_setting(inter, "anon", value))

  @settings.sub_command()
  async def info(self, inter):
    '''
    See all the settings
    '''
    e = discord.Embed(title = "Settings", description = '\n\n'.join((f"{settingkeys[k][0]}: {'✅' if v and isinstance(v, bool) else '❌' if isinstance(v, bool) else f'`{v}`'}\n> {settingkeys[k][1]}" + (f"\n> Setting ID: `{k}`" if k not in escapesetkeys else "")) for k, v in db["settings"][str(inter.author.id)].items()), color = random.randint(0, 16777215))
    e.set_footer(text = f"Link Embedder", icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png")
    await inter.send(embed = e)

  @settings.sub_command()
  async def change(self, inter, *, id: Setting, value: bool):
    '''
    Change your settings!

    Parameters
    ----------
    id: Setting id
    value: True or False
    '''
    await inter.response.defer(ephemeral = True)
    await inter.send(embed = change_setting(inter, id, value))

  @commands.slash_command()
  async def bot(self, inter):
    pass

  @bot.sub_command()
  async def ping(self, inter):
    '''
    View bot's ping
    '''
    if "/bot ping" not in db["analytics"]["day"]:
      db["analytics"]["day"]["/bot ping"] = 0
    await inter.response.defer()
    pingstart = time.time_ns()
    e = discord.Embed(title = "Loading", description = "Loading...", color = random.randint(0, 16777215))
    msg = await inter.send(embed = e)
    pingend = time.time_ns()
    e = discord.Embed(title = "Pong!", description = f"API latency: `{int(inter.bot.latency * 1000)}ms`\nLatency: `{(int(pingend - pingstart) // 1000000)}ms`\nUp since: <t:{int(inter.bot.launch_time.timestamp())}:R>", color = random.randint(0, 16777215))
    await inter.edit_original_message(embed = e)
    db["analytics"]["day"]["/bot ping"] += 1
    db["analytics"]["day"]["total"] += 1

  @bot.sub_command()
  async def info(self, inter):
    '''
    View bot's info
    '''
    if "/bot info" not in db["analytics"]["day"]:
      db["analytics"]["day"]["/bot info"] = 0
    e = discord.Embed(title = "About Link Embedder", description = "This bot turns your discord links into embeds\nMade by [@maxy_dev](https://github.com/maxy-dev).", color = random.randint(0, 16777215))
    e.add_field(name = "Bot", value = f"Total amount of commands: {len(inter.bot.slash_commands)}\nBot statistics:\n> Servers connected: `{len(inter.bot.guilds)}`\n> Users connected: `{len(inter.bot.users)}`\n> Channels connected: `{sum(len(i.channels) for i in inter.bot.guilds) - sum(len(i.categories) for i in inter.bot.guilds)}`")
    e.add_field(name = "Analytics", value = ("\n".join(f"> {key.capitalize()} {'runs' if key not in ['message embeds', 'channel embeds'] else 'ran'}: {value}" for key, value in sorted(filter(lambda v: v[1] != 0, ((k, v) for k, v in db["analytics"]["day"].items())), key = lambda v: v[1], reverse = True)) + f"\n\nResets <t:{db['analytics']['daytime']}:R>"), inline = False)
    e.add_field(name = "Links", value = "[⚡ Support me on Boosty!](https://boosty.to/number1)\n[⚡ Support me on DonationAlerts!](https://www.donationalerts.com/r/maxy1)\n[🖥️ Link Embedder Github page](https://github.com/maxy-dev/embedlink)", inline = False)
    e.add_field(name = "Versions:", value = f"Bot: `{botver}`\n[🐍 Python: `{pyver}`](https://www.python.org)\n[🧰 Disnake: `{dnver}`](https://github.com/DisnakeDev/disnake)", inline = False)
    await inter.send(embed = e)
    db["analytics"]["day"]["/bot info"] += 1
    db["analytics"]["day"]["total"] += 1

  @bot.sub_command(description = "See invites to bot support server and invite bot to your server")
  async def invite(inter):
    if "/bot invite" not in db["analytics"]["day"]:
      db["analytics"]["day"]["/bot invite"] = 0
    e = discord.Embed(title = "Invites", description = "Click the buttons below!", color = random.randint(0, 16777215))
    view = discord.ui.View()
    style = discord.ButtonStyle.gray
    item = discord.ui.Button(style = style, label = "Invite bot", url = "https://discord.com/api/oauth2/authorize?client_id=1132729065980297296&permissions=536996864&scope=bot%20applications.commands")
    item1 = discord.ui.Button(style = style, label = "Support server", url = "https://discord.gg/jRK82RNx73")
    view.add_item(item = item)
    view.add_item(item = item1)
    await inter.send(embed = e, view = view)
    db["analytics"]["day"]["/bot invite"] += 1
    db["analytics"]["day"]["total"] += 1

  @commands.slash_command()
  async def quote(self, inter, text: str = None, *, message_id: str, channel: discord.TextChannel = None):
    '''
    Embed a message using message id and channel!

    Parameters
    ----------
    text: Text you want to add
    message_id: Message id
    channel: Mention channel
    '''
    if "/quote" not in db["analytics"]["day"]:
      db["analytics"]["day"]["/quote"] = 0
    if channel is None:
      channel = inter.channel
    getmsg = await channel.fetch_message(int(message_id))
    if not getmsg:
      e = discord.Embed(title = "Error", description = "Message not found", color = random.randint(0, 16777215))
      db["analytics"]["day"]["errored"] += 1
      await inter.send(embed = e, ephemeral = True)
      return
    await inter.response.defer()
    embeds = []

    e = discord.Embed(description = getmsg.content + (("\n\n" + " | ".join(f"{reaction.emoji}` {reaction.count} `" for reaction in getmsg.reactions)) if getmsg.reactions else ''), color = random.randint(0, 16777215), timestamp = getmsg.created_at)
    if getmsg.attachments:
      e.set_image(getmsg.attachments[0])
    e.set_author(url = getmsg.jump_url, name = f"{str(getmsg.author.name)} | Click to jump", icon_url = getmsg.author.avatar if getmsg.author.avatar else f"https://cdn.discordapp.com/embed/avatars/{random.choice(list(range(0, 5)))}.png")
    e.set_footer(icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png", text = f'{dividers(["Link Embedder", f"#{getmsg.channel.name}"])}')
    embeds.append(e)
    if getmsg.embeds:
      for embed in getmsg.embeds:
        #print(embed.to_dict())
        if embed.type == "image" and not embeds[embedi].image:
          embeds[embedi].set_image(embed.thumbnail.url)
          continue
        if embed.video:
          continue
        if embed.thumbnail and embed.url:
          embed.set_image(embed.thumbnail.url + (".gif" if not embed.thumbnail.url.endswith((".gif", ".png", ".jpg", ".jpeg")) else ""))
          embed.set_thumbnail(url = None)
        embeds.append(embed)

    if getmsg.reference:
      getmsgref = getmsg.reference.resolved
      if hasattr(getmsgref, "author"):
        e = discord.Embed(description = getmsgref.content, color = random.randint(0, 16777215), timestamp = getmsgref.created_at)
        if getmsgref.attachments:
          e.set_image(getmsgref.attachments[0])
        e.set_author(url = getmsgref.jump_url, name = f"{str(getmsgref.author.name)} [Replying] | Click to jump", icon_url = getmsgref.author.avatar if getmsgref.author.avatar else f"https://cdn.discordapp.com/embed/avatars/{random.choice(list(range(0, 5)))}.png")
        e.set_footer(icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png", text = f'{dividers(["Link Embedder", f"#{getmsg.channel.name}"])}')
        embeds.append(e)
    if "message embeds" not in db["analytics"]["day"]:
      db["analytics"]["day"]["message embeds"] = 0
    db["analytics"]["day"]["message embeds"] += 1

    if embeds:
      await inter.send(content = text, embeds = embeds, allowed_mentions = discord.AllowedMentions.none())
      msgsave = await inter.original_response()
      if str(inter.author.id) not in datasaver:
        datasaver[str(inter.author.id)] = set()
      datasaver[str(inter.author.id)].add(str(msgsave.id))
      db["analytics"]["day"]["total"] += 1
      return

  @commands.slash_command()
  async def link(self, inter):
    pass

  @link.sub_command()
  async def msgbyid(self, inter, id: str, channel: discord.TextChannel):
    '''
    Get link to a message by ID in mentioned channel

    Parameters
    ----------
    id: Message ID
    channel: Channel
    '''
    if "/link msgbyid" not in db["analytics"]["day"]:
      db["analytics"]["day"]["/link msgbyid"] = 0
    fetchmsg = await channel.fetch_message(int(id))
    if not fetchmsg:
      e = discord.Embed(title = "Error", description = "Message not found", color = random.randint(0, 16777215))
      db["analytics"]["day"]["errored"] += 1
      await inter.send(embed = e, ephemeral = True)
      return

    e = discord.Embed(url = fetchmsg.jump_url, title = "Click here to jump", description = f"Normal link: {fetchmsg.jump_url}", color = random.randint(0, 16777215))
    await inter.send(embed = e, ephemeral = True)
    db["analytics"]["day"]["total"] += 1
    db["analytics"]["day"]["/link msgbyid"] += 1

  @commands.is_owner()
  @commands.slash_command()
  async def view(self, inter):
    await inter.send("```\n" + "\n".join(f"{server.owner} | {server.name} | {server.id}\n" for server in inter.bot.guilds) + "\n```")

def setup(bot):
  bot.add_cog(Utility(bot))