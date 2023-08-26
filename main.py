import asyncio
import disnake as discord
import random
import sys
import os
import topgg
import datetime, time
from utils import db, anonassign
from disnake.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()

bot = commands.InteractionBot(intents=discord.Intents.all())
bot.topgg = topgg.DBLClient(bot, os.environ["TOPGG"])

if "analytics" not in db:
  db["analytics"] = {}
  db["analytics"]["day"] = {}
  db["analytics"]["daytime"] = int(time.time()) - 86400
if "settings" not in db:
  db["settings"] = {}

@bot.event
async def on_ready():
  print("bot connected")
  print("*")
  if db["analytics"]["daytime"] < time.time():
    db["analytics"]["day"] = {"total": 0, "errored": 0}
    db["analytics"]["daytime"] = int(time.time()) + 86400
  await bot.change_presence(status = discord.Status.online, activity = discord.Game("Restarted"))
  bot.launch_time = datetime.datetime.utcnow()
  await asyncio.sleep(3)
  await bot.change_presence(status = discord.Status.online, activity = discord.Game(f"with Embeds"))

for filename in os.listdir('./cogs'):
  if filename.endswith('.py') and filename not in []:
    try:
      bot.load_extension(f'cogs.{filename[:-3]}')
    except Exception as e:
      print(f"{e.__class__.__name__}: {e}")

@tasks.loop(minutes = 30)
async def top_gg_updstats():
  try:
    await bot.topgg.post_guild_count()
    print(f"Successfully updated guild count: {len(bot.guilds)}")
  except Exception as e:
    print(f"{e.__class__.__name__}: {e}")

@tasks.loop(minutes = 5)
async def reset_anon():
  try:
    anonassign = {}
  except Exception as e:
    print(f"{e.__class__.__name__}: {e}")

@tasks.loop(hours = 1)
async def check_timeout():
  try:
    if db["analytics"]["daytime"] < time.time():
      db["analytics"]["day"] = {"total": 0, "errored": 0}
      db["analytics"]["daytime"] = int(time.time()) + 86400
  except Exception as e:
    print(f"{e.__class__.__name__}: {e}")

if os.environ["TEST"] != "y":
  top_gg_updstats.start()
check_timeout.start()
reset_anon.start()
bot.run(os.environ["DISCORD_TOKEN"])