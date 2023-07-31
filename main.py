import asyncio
import disnake as discord
import random
import sys
import os
import datetime, time
from utils import db
from disnake.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()

bot = commands.InteractionBot(intents=discord.Intents.all())

if "analytics" not in db:
  db["analytics"] = {}
if "day" not in db["analytics"]:
  db["analytics"]["day"] = {}
if "daytime" not in db["analytics"]:
  db["analytics"]["daytime"] = int(time.time()) - 86400

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

@tasks.loop(hours = 1)
async def check_timeout():
  try:
    if db["analytics"]["daytime"] < time.time():
      db["analytics"]["day"] = {"total": 0, "errored": 0}
      db["analytics"]["daytime"] = int(time.time()) + 86400
  except Exception as e:
    print(f"{e.__class__.__name__}: {e}")


check_timeout.start()
bot.run(os.environ["DISCORD_TOKEN"])