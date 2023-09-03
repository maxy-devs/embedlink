from typing import Union
import datetime, time
import disnake as discord
from disnake.ext import commands
from typing import Dict, Any
import redis as rd
import json
import os
import atexit
import random
import asyncio
from dotenv import load_dotenv
load_dotenv()

class Singleton(type):
  _instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]

class Database(dict):
  def __init__(self, directory: str = "./", filename: str = "db.json"):
      self.__fullpath = directory + filename
      super().__init__()
      self.file = JsonFile(self.__fullpath)
      self.backup = JsonFile(f"{directory}backup.json")
      self.dict = self.file
      atexit.register(self.__del)

  def __getitem__(self, key):
      return self.dict[key]

  def __setitem__(self, key, value):
      self.dict[key] = value

  def __repr__(self):
      return self.dict.__repr__()

  def __contains__(self, item):
      return item in self.dict

  def __del(self):
      self.file = self.dict
      self.backup = self.dict
      self.file.save()
      self.backup.save()

def Embed(
    msg: Union[commands.Context, discord.Interaction, discord.Message],
    description: str = '',
    title: str = '',
    fields: list = [],
    footer: dict = {},
    image: dict = {},
    image_url: str = None,
    thumbnail: dict = {},
    thumbnail_url: str = None,
    video: dict = {},
    video_url: str = None,
    author: dict = {},
    type: str = 'rich',
    timestamp: datetime.datetime = None,
    color: Union[discord.Colour, int] = None,
    colour: Union[discord.Colour, int] = None):
    return discord.Embed.from_dict(
        {
        'title': title,
        'description': description,
        'footer': footer,
        'fields': fields,
        'image': {'url': image_url} if image_url else image,
        'thumbnail': {'url': thumbnail_url} if thumbnail_url else thumbnail,
        'video': {'url': video_url} if video_url else video,
        'author': author if author else {'name': msg.command.name.title() if (isinstance(msg, commands.Context) and msg.command) else msg.data.name.title() if isinstance(msg, discord.Interaction) else '',
        'icon_url': 'https://cdn.discordapp.com/attachments/914750432520331304/933032744349474836/carbot.png'} if isinstance(msg, (commands.Context, discord.Interaction)) else {},
        'type': type,
        'timestamp': timestamp,
        'color': color if color else colour if colour else None
      }
    )

class JsonFile(object):
  _var: Dict[Any, Any]
  def __init__(self, filename):
    self.filename = filename
    self._var = {}
    self.load()

  def __getitem__(self, item):
    return self._var[item]

  def __setitem__(self, key, value):
    self._var[key] = value

  def __contains__(self, item):
    return item in self._var

  def load(self):
    try:
        with open(self.filename, 'r') as f:
            self._var = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        with open(self.filename, 'w') as f:
            json.dump({}, f)

  def save(self):
    with open(self.filename, "w") as f:
      json.dump(self._var, f, indent = 4)

class RDBLive(object):
  def __init__(self, name: str = "main", key: str = None, *, host: str, port: int, password: str, client_name: str, charset: str = "utf-8", decode_responses: bool = True, dont_save: bool = False):
    super().__init__()
    self._redis = rd.Redis(host = host, port = port, password = password, client_name = client_name, charset = charset, decode_responses = decode_responses, health_check_interval = 1000)
    atexit.register(self.__del)
    self._backup = JsonFile("backup.json")
    self._eventloop = asyncio.new_event_loop()
    self.__ds = dont_save
    self.__break = False
    self._var = {}
    self._oldvar = {}
    self._name = name
    self._key = key if key else name
    self.__load()

  def __getitem__(self, item):
    print(f"getitem {item} {self._var == self._oldvar}")
    if not self.__ds:
      if self._var != self._oldvar:
        self._redis.hset(self._name, self._key, json.dumps(self._var))
        self._oldvar = json.loads(self._redis.hget(self._name, self._key))
    return self._var[item]

  def __setitem__(self, key, value):
    print(f"setitem {key} {value} {self._var == self._oldvar}")
    self._var[key] = value
    if not self.__ds:
      if self._var != self._oldvar:
        self._redis.hset(self._name, self._key, json.dumps(self._var))
        self._oldvar = json.loads(self._redis.hget(self._name, self._key))

  # def __getattr__(self, item):
  #   if item not in self._var:
  #     return object.__getattribute__(self, item)
  #   else:
  #     return self._var[item]
  #
  # def __setattr__(self, key, value):
  #   if key in dir(self):
  #     raise Exception("You cannot change internal attributes")
  #   if key.startswith("_"):
  #     object.__setattr__(self, key, value)
  #   else:
  #     self._var[key] = value

  def __repr__(self):
    return self._var.__repr__()

  def __contains__(self, item):
    print(f"contains {item} {self._var == self._oldvar}")
    if not self.__ds:
      if self._var != self._oldvar:
        self._redis.hset(self._name, self._key, json.dumps(self._var))
        self._oldvar = json.loads(self._redis.hget(self._name, self._key))
    return item in self._var

  def __load(self):
    print("load")
    if not self._redis.hexists(self._name, self._key):
      self._redis.hset(self._name, self._key, "{}")
    if self._var == {}:
      self._backup.load()
      if "crashed" in self._backup:
        if self._backup["crashed"]:
          self._backup["crashed"] = False
          self._backup.save()
          self._var = self._backup
        else:
          self._var = json.loads(self._redis.hget(self._name, self._key))
      else:
        self._var = json.loads(self._redis.hget(self._name, self._key))

  def __del(self):
    print("del")
    if not self.__ds:
      try:
        self._redis.hset(self._name, self._key, json.dumps(self._var))
      except Exception as e:
        print(e)
        self._var["crashed"] = True
        self._backup = self._var
        self._backup.save()
    self._redis.close()

async def Webhook(ctx, channel = None):
  if ctx != None:
    if channel != None:
      for webhook in (await channel.webhooks()):
        if webhook.user.id == ctx.bot.user.id and webhook.name == "Link Embedder Webhook":
          return webhook
      return (await channel.create_webhook(name="Link Embedder Webhook"))

    for webhook in (await ctx.channel.webhooks()):
      if webhook.user.id == ctx.bot.user.id and webhook.name == "Link Embedder Webhook":
        return webhook
    return (await ctx.channel.create_webhook(name="Link Embedder Webhook"))

def dividers(array: list, divider: str = " | "):
  ft = []
  for i in array:
    if i:
      ft.append(i)
  return divider.join(ft) if divider else ""

datasaver = {}
defaultset = {"msg_ignore_unknown": False, "msg_ignore_all": False, "no_embed_on_mention": False, "anon": False, "send_as_bot": False}
anonassign = {}


dontsave = True
if os.environ["TEST"] != "y":
  dontsave = False

db = None
try:
  db = RDBLive("embedlink", "embedlink", host = os.environ["REDISHOST"], port = os.environ["REDISPORT"], password = os.environ["REDISPASSWORD"], client_name = None, dont_save = dontsave)
except (Exception, rd.exceptions.TimeoutError) as e:
  print(e)
  db = Database()