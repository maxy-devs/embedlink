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
      self.dict = self.file.data
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
      self.file.data = self.dict
      self.backup.data = self.dict
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
  __data: Dict[Any, Any]
  def __init__(self, filename):
      self.filename = filename
      self.__data = {}
      self.load()

  def __enter__(self):
      return self.__data

  def __exit__(self, exc_type, exc_val, exc_tb):
      self.save()

  def __contains__(self, item):
      return item in self.__data

  def load(self):
      try:
          with open(self.filename, 'r') as f:
              self.__data = json.load(f)
      except (FileNotFoundError, json.decoder.JSONDecodeError):
          with open(self.filename, 'w') as f:
              json.dump({}, f)

  def save(self):
      with open(self.filename, "w") as f:
          json.dump(self.__data, f, indent = 4)

  @property
  def data(self):
      return self.__data

  @data.setter
  def data(self, value):
      self.__data = value

class RedisDBLive(dict):
  def __init__(self, name: str = "main", key: str = None, *, host: str, port: int, password: str, client_name: str, charset: str = "utf-8", decode_responses: bool = True, dont_save: bool = False):
    super().__init__()
    self._redis = rd.Redis(host = host, port = port, password = password, client_name = client_name, charset = charset, decode_responses = decode_responses, health_check_interval = 1000)
    atexit.register(self.__del)
    self._backup = JsonFile("backup.json")
    self.__ds = dont_save
    self._name = name
    self._var = {}
    self._key = key if key else name
    self.__load()

  def __getitem__(self, item):
    # if self._var == {}:
    #   self._var = json.loads(self._redis.hget(self._name, self._key))
    return self._var[item]

  def __setitem__(self, key, value):
    self._var[key] = value
    if not self.__ds:
      self._redis.hset(self._name, self._key, json.dumps(self._var))

  def __contains__(self, item):
    # if self._var == {}:
    #   self._var = json.loads(self._redis.hget(self._name, self._key))
    return item in self._var

  def __repr__(self):
    return self._var.__repr__()
      
  def __del(self):
    if not self.__ds:
      try:
        self._redis.hset(self._name, self._key, json.dumps(self._var))
      except Exception as e:
        print(e)
        self._var["crashed"] = True
        self._backup.data = self._var
        self._backup.save()
    self._redis.close()

  def __load(self):
    if self._var == {}:
      if "crashed" in self._backup.data:
        if self._backup.data["crashed"]:
          del self._backup.data["crashed"]
          self._var = self._backup.data
        else:
          self._var = json.loads(self._redis.hget(self._name, self._key))
      else:
        self._var = json.loads(self._redis.hget(self._name, self._key))


class RedisDB(dict):
  def __init__(self, name: str = "main", key: str = None, *, host: str, port: int, password: str, client_name: str, charset: str = "utf-8", decode_responses: bool = True, dont_save: bool = False):
    self._redis = rd.Redis(host = host, port = port, password = password, client_name = client_name, charset = charset, decode_responses = decode_responses, health_check_interval = 1000)
    super().__init__()
    self._backup = JsonFile("backup.json")
    self._name = name
    self.__ds = dont_save
    self._key = key if key else name
    self._var = self._load(True)
    atexit.register(self.__del)

  def __getitem__(self, key):
      return self._var[key]

  def __setitem__(self, key, value):
      self._var[key] = value
      if not self.__ds:
        self._save()

  def __repr__(self):
      return self._var.__repr__()

  def __enter__(self) -> dict:
      return self._load()

  def __exit__(self, exc_type, exc_value, exc_traceback):
      if not self.__ds:
        self._save()

  def __contains__(self, item):
      return item in self._var

  def _load(self, backup = False):
      if self._key not in self._redis.keys():
          self._redis.hset(self._name, self._name, "{}")
      self._var = json.loads(self._redis.hget(self._name, self._key))
      if backup:
          if self._var != self._backup.data and self._backup.data:
              self._var = self._backup.data
              self._backup.data = {}
              self._backup.save()
      return self._var

  def _save(self):
      try:
          if self._var != json.loads(self._redis.hget(self._name, self._key)):
              self._redis.hset(self._name, self._key, json.dumps(self._var))
      except Exception:
          self._backup.data = self._var
          self._backup.save()

  def __del(self):
      if not self.__ds:
          self._save()
      self._redis.close()

async def Webhook(ctx, channel = None):
  if ctx != None:
    if channel != None:
      for webhook in (await channel.webhooks()):
        if webhook.user.id == ctx.bot.user.id and webhook.name == "PythonBot Webhook":
          return webhook
      return (await channel.create_webhook(name="PythonBot Webhook"))

    for webhook in (await ctx.channel.webhooks()):
      if webhook.user.id == ctx.bot.user.id and webhook.name == "PythonBot Webhook":
        return webhook
    return (await ctx.channel.create_webhook(name="PythonBot Webhook"))

def dividers(array: list, divider: str = " | "):
  ft = []
  for i in array:
    if i:
      ft.append(i)
  return divider.join(ft) if divider else ""

dontsave = True
if os.environ["TEST"] != "y":
  dontsave = False

db = None
try:
  db = RedisDBLive("embedlink", "embedlink", host = os.environ["REDISHOST"], port = os.environ["REDISPORT"], password = os.environ["REDISPASSWORD"], client_name = None, dont_save = dontsave)
except (Exception, rd.exceptions.TimeoutError):
  db = Database()
