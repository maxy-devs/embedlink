#cog by @maxy_dev (maxy#2866)
import asyncio
import disnake as discord
import random
import os
import re
import datetime, time
from disnake.ext import commands
from utils import db, dividers, datasaver, defaultset, anonassign
import utils

icons = {"TextChannel": "#️⃣",
         "VoiceChannel": "🔊",
         "Thread": "🧵",
         "StageChannel": "🎙️",
         "ForumChannel": "💬"}

class Events(commands.Cog):
  def __init__(self, bot: commands.InteractionBot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, msg: discord.Message):
    if msg.author.bot:
      return

    if str(msg.author.id) not in db["settings"]:
      db["settings"][str(msg.author.id)] = defaultset.copy()
    else:
      for i in defaultset.keys():
        if i not in db["settings"][str(msg.author.id)]:
          db["settings"][str(msg.author.id)][i] = False

    if db["settings"][str(msg.author.id)]["msg_ignore_all"]:
      return

    if self.bot.user.mention in msg.content and not db["settings"][str(msg.author.id)]["no_embed_on_mention"]:
      e = discord.Embed(title = "Hello!", description = "Im Link Embedder and i can embed your discord links!\nJust copy a message/channel link and send it in the chat!\n\nPut any symbol before the link to cancel the embed", color = random.randint(0, 16777215))
      e.set_image("https://cdn.discordapp.com/attachments/843562496543817781/1135674485295550464/gmDLvizIwzgL.gif")
      e.set_footer(text = f"Link Embedder", icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png")
      await msg.reply(embed = e)
      return

    #if "https://discord.com/channels/" in msg.content:
    if re.findall("https?://(ptb\.|canary\.)?discord(app)?\.com/channels/", msg.content):
      links = msg.content.replace("\n", " \n ").split(" ")
      embeds = []
      embedcount = 0
      embedi = -1
      getmsg = None
      oneanon = None
      for n, i in enumerate(links):
        ids = re.findall("[0-9]{10,}", i.strip())
        anon = False
        refanon = False
        if not links[n].startswith("http"):
          continue

        if len(ids) == 3:
          getmsg = None
          try:
            getmsg: discord.Message = await (self.bot.get_channel(int(ids[1])).fetch_message(int(ids[2])))
          except (discord.NotFound, AttributeError):
            getmsg = None
          if not getmsg:
            if not db["settings"][str(msg.author.id)]["msg_ignore_unknown"]:
              embedcount += 1
              e = discord.Embed(description = f"Message not found\nLink: {links[n]}" + f"{' (ptb)' if 'ptb' in i else ''}{(' (canary)' if 'canary' in i else '')}{(' (discordapp)' if 'discordapp' in i else '')}", color = 0xED4245)
              e.set_footer(text = f"Link Embedder", icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png")
              links[n] = f"[Embed #{embedcount}]"
              embeds.append(e)
              db["analytics"]["day"]["errored"] += 1
            continue

          if str(getmsg.author.id) not in db["settings"]:
            db["settings"][str(getmsg.author.id)] = defaultset.copy()
          else:
            for key in defaultset.keys():
              if key not in db["settings"][str(getmsg.author.id)]:
                db["settings"][str(getmsg.author.id)][key] = False

          if db["settings"][str(getmsg.author.id)]["anon"] or getmsg.author.name in anonassign:
            if str(getmsg.author.id) not in anonassign:
              while True:
                randomize = str(random.randint(1, len(self.bot.users)))
                if randomize in anonassign.values():
                  continue
                anonassign[str(getmsg.author.id)] = randomize
                if not getmsg.author.name in anonassign:
                  anonassign[getmsg.author.name] = randomize
                break
            anon = True
            if not oneanon:
              oneanon = True
            if db["settings"][str(getmsg.author.id)]["anon"] == "servers you arent in":
              if msg.guild in getmsg.author.mutual_guilds:
                anon = False
                oneanon = False
          embedcount += 1
          embedi += 1
          links[n] = f"[Embed #{embedcount}]"
          e = discord.Embed(description = getmsg.content + (("\n\n" + " | ".join(f"{reaction.emoji}` {reaction.count} `" for reaction in getmsg.reactions)) if getmsg.reactions else ''), color = random.randint(0, 16777215), timestamp = getmsg.created_at)
          if getmsg.attachments:
            e.set_image(getmsg.attachments[0])
          e.set_author(url = getmsg.jump_url if not anon else None, name = (f"{str(getmsg.author.name)}" if not anon else f"User #{anonassign[str(getmsg.author.id)]}") + ((" | Click to jump" + f"{' (ptb)' if 'ptb' in i else ''}{(' (canary)' if 'canary' in i else '')}{(' (discordapp)' if 'discordapp' in i else '')}") if not anon else ""), icon_url = getmsg.author.avatar if getmsg.author.avatar and not anon else f"https://cdn.discordapp.com/embed/avatars/{random.choice(list(range(0, 5)))}.png")
          e.set_footer(icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png", text = f'{dividers(["Link Embedder", f"#{getmsg.channel.name}" if not anon else None, getmsg.guild.name if getmsg.guild != msg.guild and not anon else ""])}')
          embeds.append(e)
          if getmsg.embeds:
            embedcount += len(getmsg.embeds)
            for embed in getmsg.embeds:
              #print(embed.to_dict())
              if embed.type == "image" and not embeds[embedi].image:
                embeds[embedi].set_image(embed.thumbnail.url)
                continue
              if embed.video:
                embedcount -= 1
                continue
              if embed.thumbnail and embed.url:
                embed.set_image(embed.thumbnail.url + (".gif" if not embed.thumbnail.url.endswith((".gif", ".png", ".jpg", ".jpeg")) else ""))
                embed.set_thumbnail(url = None)
              embeds.append(embed)

          if getmsg.reference:
            getmsgref = getmsg.reference.resolved
            if hasattr(getmsgref, "author"):
              if db["settings"][str(getmsgref.author.id)]["anon"] or getmsgref.author.name in anonassign:
                if str(getmsgref.author.id) not in anonassign:
                  while True:
                    randomize = str(random.randint(1, len(self.bot.users)))
                    if randomize in anonassign.values():
                      continue
                    anonassign[str(getmsgref.author.id)] = randomize
                    if not getmsgref.author.name in anonassign:
                      anonassign[getmsgref.author.name] = randomize
                    break
                refanon = True
                if not oneanon:
                  oneanon = True
                if db["settings"][str(getmsgref.author.id)]["anon"] == "servers you arent in":
                  if msg.guild in getmsgref.author.mutual_guilds:
                    anon = False
                    oneanon = False
              if refanon:
                embeds[embedi].set_author(name = (f"{str(getmsg.author.name)}" if not anon else f"User #{anonassign[str(getmsg.author.id)]}"), icon_url = getmsg.author.avatar if getmsg.author.avatar and not anon else f"https://cdn.discordapp.com/embed/avatars/{random.choice(list(range(0, 5)))}.png")
                embeds[embedi].set_footer(icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png", text = "Link Embedder")
              ref = discord.Embed(description = getmsgref.content, color = random.randint(0, 16777215), timestamp = getmsgref.created_at)
              if getmsgref.attachments:
                ref.set_image(getmsgref.attachments[0])
              ref.set_author(url = getmsgref.jump_url if not refanon else None, name = (f"{str(getmsgref.author.name)}" if not refanon else f"User #{anonassign[str(getmsgref.author.id)]}") + ((" | Click to jump" + f"{' (ptb)' if 'ptb' in i else ''}{(' (canary)' if 'canary' in i else '')}{(' (discordapp)' if 'discordapp' in i else '')}") if not refanon and not anon else ""), icon_url = getmsgref.author.avatar if getmsgref.author.avatar and not refanon else f"https://cdn.discordapp.com/embed/avatars/{random.choice(list(range(0, 5)))}.png")
              ref.set_footer(icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png", text = f'{dividers(["Link Embedder", f"#{getmsg.channel.name}" if not anon and not refanon else None, getmsg.guild.name if getmsg.guild != msg.guild and not anon and not refanon else ""])}')
              embeds.append(ref)
              embedcount += 1
          if "message embeds" not in db["analytics"]["day"]:
            db["analytics"]["day"]["message embeds"] = 0
          db["analytics"]["day"]["message embeds"] += 1

        elif len(ids) == 2:
          getchnl = self.bot.get_channel(int(ids[1]))
          if not getchnl:
            embedcount += 1
            e = discord.Embed(description = f"Channel not found\nLink: {links[n]}", color = 0xED4245)
            e.set_footer(text = f"Link Embedder", icon_url = "https://cdn.discordapp.com/attachments/843562496543817781/1134933097314537632/8rGXVQ2FXq9W.png")
            links[n] = f"[Embed #{embedcount}]"
            embeds.append(e)
            db["analytics"]["day"]["errored"] += 1
            continue
          embedcount += 1
          links[n] = f"[Embed #{embedcount}]"
          e = discord.Embed(url = getchnl.jump_url, title = f"Channel Embed (Click to jump)", description = (f"# ▼ {getchnl.category}\n" if getchnl.category else "") + f"##{'#' if getchnl.__class__.__name__ == 'Thread' and getchnl.guild == msg.guild else ''} [`{(getchnl.guild.name + ' > ') if getchnl.guild != msg.guild else ''}" + ((f"{(icons[getchnl.parent.__class__.__name__] if not (getchnl.parent.is_news() if hasattr(getchnl.parent, 'is_news') else False) else '📢') if not (getchnl.parent.is_nsfw() if hasattr(getchnl.parent, 'is_nsfw') else False) else '🔞'}{getchnl.parent.name}`]({getchnl.parent.jump_url})" + '\n## [`╰━ ') if getchnl.__class__.__name__ == 'Thread' and getchnl.guild == msg.guild else '') + f"{(icons[getchnl.__class__.__name__] if not (getchnl.is_news() if hasattr(getchnl, 'is_news') else False) else '📢') if not (getchnl.is_nsfw() if hasattr(getchnl, 'is_nsfw') else False) else '🔞'}{getchnl.name}`]({getchnl.jump_url})" + ((f"\n> " + getchnl.topic.replace("\n", "\n> ")) if hasattr(getchnl, "topic") and getchnl.topic else "") + ((f" ({len(getchnl.members)})\nCurrent members in the voice chat:\n> " + "\n> ".join(f"{member.name}" for member in getchnl.members) if getchnl.members else '\nCurrently empty') if getchnl.__class__.__name__ in ["VoiceChannel", "StageChannel"] else ''), color = random.randint(0, 16777215), timestamp = getchnl.created_at)
          e.set_footer(text = dividers([f"ID: {getchnl.id}", "Link Embedder"]))
          embeds.append(e)
          if "channel embeds" not in db["analytics"]["day"]:
            db["analytics"]["day"]["channel embeds"] = 0
          db["analytics"]["day"]["channel embeds"] += 1

      if len(embeds) > 10:
        e = discord.Embed(title = "Error", description = "Total amount of embeds was more than 10\nPlease try again but with a single link", color = random.randint(0, 16777215))
        db["analytics"]["day"]["errored"] += 1
        await msg.reply(embed = e)
        return

      if embeds:
        content = " ".join(links)
        content = content.replace(" \n ", "\n")
        webhook = None
        if hasattr(msg.channel, "webhooks"):
          if msg.channel.permissions_for(msg.guild.me).manage_webhooks:
            webhook = (await utils.Webhook((commands.Context(message = msg, bot = self.bot, view = None))))
        msgref = None
        if msg.reference:
          msgref = msg.reference.resolved
          if not hasattr(msgref, "author"):
            msgref = None
        msgsave = None
        if webhook:
          await msg.delete()
          msgsave = await webhook.send(content = (f'╭━  [`@{msgref.author.name}`: ' + (msgref.content[0:49].replace("\n", " ")) + f']({msgref.jump_url})\n' if msgref else "") + content if content else None, embeds = embeds, username = msg.author.name, avatar_url = msg.author.avatar, allowed_mentions = discord.AllowedMentions.none(), wait = True)
        else:
          if oneanon:
            await msg.delete()
          msgsave = await msg.channel.send(content = (f'╭━  [`@{msgref.author.name}`: ' + (msgref.content[0:49].replace("\n", " ")) + f']({msgref.jump_url})\n' if msgref else "") + (f"`{msg.author.name}:` ") + content if content else None, embeds = embeds, allowed_mentions = discord.AllowedMentions.none())
        if str(msg.author.id) not in datasaver:
          datasaver[str(msg.author.id)] = set()
        datasaver[str(msg.author.id)].add(str(msgsave.id))
        db["analytics"]["day"]["total"] += 1
        return

  @commands.Cog.listener()
  async def on_slash_command_error(self, inter, error):
    if isinstance(error, commands.CommandNotFound):
      return
    if not isinstance(error, commands.CommandOnCooldown):
      if not "Command raised an exception:" in str(error):
        e = discord.Embed(title = "Error", description = f"```{str(error)}```", color = random.randint(0, 16777215))
      else:
        e = discord.Embed(title = "Error", description = f"```{str(error)[29:]}```", color = random.randint(0, 16777215))
    else:
      e = discord.Embed(title = "Error", description = f"{str(error)[:31]} <t:{int(time.time() + error.retry_after)}:R>", color = random.randint(0, 16777215))
    await inter.send(embed = e, ephemeral = True)
    db["analytics"]["day"]["errored"] += 1
def setup(bot):
  bot.add_cog(Events(bot))