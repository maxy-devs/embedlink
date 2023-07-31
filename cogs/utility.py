#cog by @maxy_dev (maxy#2866)
import asyncio
import disnake as discord
import random
import os, sys
import datetime, time
from disnake.ext import commands
from utils import db

botver = "4.2.6"
pyver = ".".join(str(i) for i in list(sys.version_info)[0:3])
dnver = ".".join(str(i) for i in list(discord.version_info)[0:3])



class Utility(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

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