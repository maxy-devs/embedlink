#cog by @maxy_dev (maxy#2866)
import asyncio
import disnake as discord
import random
import os, sys
import datetime, time
from disnake.ext import commands
from utils import db, datasaver, defaultset

botver = "4.6.0"
pyver = ".".join(str(i) for i in list(sys.version_info)[0:3])
dnver = ".".join(str(i) for i in list(discord.version_info)[0:3])

settingkeys = {"msg_ignore_unknown": ("Ignore unknown message links", "Self explanatory"),
               "no_embed_on_mention": ("No embed on mention", "No 'Hello!' embed when you mention the bot"),
               "msg_ignore_all": ("Ignore messages", "Ignores all of your links and messages")}

async def suggest_setting(inter, input):
  if str(inter.author.id) not in db["settings"]:
    db["notes"][str(inter.author.id)] = defaultset
  return [setting for setting in list(db['settings'][str(inter.author.id)].keys()) if input.lower() in setting.lower()][0:24]


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
      db["settings"][str(inter.author.id)] = defaultset

  @settings.sub_command()
  async def info(self, inter):
    '''
    See all the settings
    '''
    e = discord.Embed(title = "Settings", description = '\n\n'.join(f"{settingkeys[k][0]}: {'✅' if v else '❌'}\n> {settingkeys[k][1]}\n> Setting ID: `{k}`" for k, v in db["settings"][str(inter.author.id)].items()), color = random.randint(0, 16777215))
    e.set_footer(text = f"Link Embedder", icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png")
    await inter.send(embed = e)

  @settings.sub_command()
  async def change(self, inter, *, id: str = commands.Param(autocomplete = suggest_setting), value: bool):
    '''
    Change your settings!

    Parameters
    ----------
    id: Setting id
    value: True or False
    '''
    if id not in db["settings"][str(inter.author.id)]:
      e = discord.Embed(title = "Error", description = "This setting does not exist\nMaybe you misspelled the setting id?", color = random.randint(0, 16777215))
      await inter.send(embed = e, ephemeral = True)
      return
    if value == db["settings"][str(inter.author.id)][id]:
      e = discord.Embed(title = "Error", description = "This setting is already set to this value", color = random.randint(0, 16777215))
      await inter.send(embed = e, ephemeral = True)
      return
    db["settings"][str(inter.author.id)][id] = value
    e = discord.Embed(title = "Success", description = "Setting updated!", color = random.randint(0, 16777215))
    await inter.send(embed = e, ephemeral = True)

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
  async def link(self, inter):
    pass

  @link.sub_command()
  async def msgbyid(self, inter, id: str):
    '''
    Get link to a message by ID in current channel

    Parameters
    ----------
    id: Message ID
    '''
    if "/link msgbyid" not in db["analytics"]["day"]:
      db["analytics"]["day"]["/link msgbyid"] = 0
    fetchmsg = await inter.channel.fetch_message(int(id))
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