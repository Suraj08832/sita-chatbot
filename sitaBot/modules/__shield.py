#    Copyright (C) DevsExpo 2020-2021
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import asyncio
import logging
import os
import re

import better_profanity
import emoji
# import nude  # nudepy not available - commented out
import requests
from better_profanity import profanity
from google_trans_new import google_translator
from telethon import events
from telethon.tl.types import ChatBannedRights

from sitaBot import BOT_ID
from sitaBot.conf import get_int_key, get_str_key

# from sitaBot.db.mongo_helpers.nsfw_guard import add_chat, get_all_nsfw_chats, is_chat_in_db, rm_chat
from sitaBot.pyrogramee.telethonbasics import is_admin
from sitaBot.events import register
from sitaBot import MONGO_DB_URI
from pymongo import MongoClient
from sitaBot.modules.sql_extended.nsfw_watch_sql import (
    add_nsfwatch,
    get_all_nsfw_enabled_chat,
    is_nsfwatch_indb,
    rmnsfwatch,
)
from sitaBot import telethn as tbot, pbot
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus

translator = google_translator()
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

# Extract database name from URI or default to destinymusic
_db_name = "destinymusic"
if MONGO_DB_URI and "/" in MONGO_DB_URI.split("?")[0]:
    try:
        _db_name = MONGO_DB_URI.split("/")[-1].split("?")[0] or _db_name
    except Exception:
        pass

client = MongoClient(MONGO_DB_URI) if MONGO_DB_URI else None
db = client[_db_name] if client else None

async def is_nsfw(event):
    lmao = event
    if not (
        lmao.gif
        or lmao.video
        or lmao.video_note
        or lmao.photo
        or lmao.sticker
        or lmao.media
    ):
        return False
    if lmao.video or lmao.video_note or lmao.sticker or lmao.gif:
        try:
            starkstark = await event.client.download_media(lmao.media, thumb=-1)
        except:
            return False
    elif lmao.photo or lmao.sticker:
        try:
            starkstark = await event.client.download_media(lmao.media)
        except:
            return False
    img = starkstark
    f = {"file": (img, open(img, "rb"))}

    r = requests.post("https://starkapi.herokuapp.com/nsfw/", files=f).json()
    if r.get("success") is False:
        is_nsfw = False
    elif r.get("is_nsfw") is True:
        is_nsfw = True
    elif r.get("is_nsfw") is False:
        is_nsfw = False
    return is_nsfw


# Pyrogram handler for gshield
@pbot.on_message(filters.command("gshield") & filters.group & ~filters.bot)
async def gshield_pyrogram(client, message):
    try:
        if not message.chat:
            return
        
        # Check if bot is admin
        try:
            bot_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
            if bot_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                await message.reply_text("`I Should Be Admin To Do This!`")
                return
        except Exception:
            await message.reply_text("`I Should Be Admin To Do This!`")
            return
        
        # Check if user is admin
        try:
            user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                await message.reply_text("`You Should Be Admin To Do This!`")
                return
        except Exception:
            await message.reply_text("`You Should Be Admin To Do This!`")
            return
        
        if len(message.command) < 2:
            await message.reply_text("Usage: `/gshield on` or `/gshield off`")
            return
        
        input_str = message.command[1].lower()
        chat_id_str = str(message.chat.id)
        
        if input_str in ("on", "enable"):
            if is_nsfwatch_indb(chat_id_str):
                await message.reply_text("`This Chat Has Already Enabled Nsfw Watch.`")
                return
            add_nsfwatch(chat_id_str)
            await message.reply_text(
                f"**Added Chat {message.chat.title} With Id {message.chat.id} To Database. This Groups Nsfw Contents Will Be Deleted**"
            )
        elif input_str in ("off", "disable"):
            if not is_nsfwatch_indb(chat_id_str):
                await message.reply_text("This Chat Has Not Enabled Nsfw Watch.")
                return
            rmnsfwatch(chat_id_str)
            await message.reply_text(
                f"**Removed Chat {message.chat.title} With Id {message.chat.id} From Nsfw Watch**"
            )
        else:
            await message.reply_text(
                "I understand `/gshield on` and `/gshield off` only"
            )
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")


# Telethon handler (kept for compatibility)
@tbot.on(events.NewMessage(pattern="/gshield (.*)"))
async def nsfw_watch(event):
    if not event.is_group:
        await event.reply("You Can Only Nsfw Watch in Groups.")
        return
    input_str = event.pattern_match.group(1)
    if not await is_admin(event, BOT_ID):
        try:
            await event.reply("`I Should Be Admin To Do This!`")
        except Exception:
            pass  # Ignore ChannelPrivateError or other errors
        return
    if await is_admin(event, event.message.sender_id):
        if (
            input_str == "on"
            or input_str == "On"
            or input_str == "ON"
            or input_str == "enable"
        ):
            if is_nsfwatch_indb(str(event.chat_id)):
                await event.reply("`This Chat Has Already Enabled Nsfw Watch.`")
                return
            add_nsfwatch(str(event.chat_id))
            await event.reply(
                f"**Added Chat {event.chat.title} With Id {event.chat_id} To Database. This Groups Nsfw Contents Will Be Deleted**"
            )
        elif (
            input_str == "off"
            or input_str == "Off"
            or input_str == "OFF"
            or input_str == "disable"
        ):
            if not is_nsfwatch_indb(str(event.chat_id)):
                await event.reply("This Chat Has Not Enabled Nsfw Watch.")
                return
            rmnsfwatch(str(event.chat_id))
            await event.reply(
                f"**Removed Chat {event.chat.title} With Id {event.chat_id} From Nsfw Watch**"
            )
        else:
            await event.reply(
                "I undestand `/gshield on` and `/gshield off` only"
            )
    else:
        await event.reply("`You Should Be Admin To Do This!`")
        return


@tbot.on(events.NewMessage())
async def ws(event):
    warner_starkz = get_all_nsfw_enabled_chat()
    if len(warner_starkz) == 0:
        return
    if not is_nsfwatch_indb(str(event.chat_id)):
        return
    if not (event.photo):
        return
    if not await is_admin(event, BOT_ID):
        return
    if await is_admin(event, event.message.sender_id):
        return
    sender = await event.get_sender()
    await event.client.download_media(event.photo, "nudes.jpg")
    if nude.is_nude("./nudes.jpg"):
        await event.delete()
        st = sender.first_name
        hh = sender.id
        final = f"**NSFW DETECTED**\n\n{st}](tg://user?id={hh}) your message contain NSFW content.. So, Sita deleted the message\n\n **Nsfw Sender - User / Bot :** {st}](tg://user?id={hh})  \n\n`⚔️Automatic Detections Powered By Sita AI` \n**#GROUP_GUARDIAN** "
        dev = await event.respond(final)
        await asyncio.sleep(10)
        await dev.delete()
        os.remove("nudes.jpg")


# Pyrogram NSFW filter for gshield
async def is_nsfw_pyrogram(client, message):
    """Check if message contains NSFW content using API"""
    try:
        if not (message.photo or message.video or message.document or message.sticker or message.animation):
            return False
        
        # Download media
        try:
            if message.photo:
                file_path = await message.download()
            elif message.video or message.animation:
                file_path = await message.download()
            elif message.sticker:
                file_path = await message.download()
            elif message.document:
                file_path = await message.download()
            else:
                return False
        except Exception:
            return False
        
        # Check using API
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "image/jpeg")}
                r = requests.post("https://starkapi.herokuapp.com/nsfw/", files=files, timeout=10)
                data = r.json() if r.status_code == 200 else {}
                
            # Clean up file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
            
            if data.get("success") is False:
                return False
            elif data.get("is_nsfw") is True:
                return True
            else:
                return False
        except Exception:
            try:
                os.remove(file_path)
            except Exception:
                pass
            return False
    except Exception:
        return False


@pbot.on_message(filters.media & filters.group & ~filters.private & ~filters.bot, group=2)
async def nsfw_filter_pyrogram(client, message):
    """Filter NSFW content when gshield is enabled"""
    try:
        # Check if gshield is enabled for this chat
        if not is_nsfwatch_indb(str(message.chat.id)):
            return
        
        # Check if bot is admin
        try:
            bot_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
            if bot_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                return
        except Exception:
            return
        
        # Skip if sender is admin
        try:
            user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                return
        except Exception:
            pass
        
        # Check for NSFW
        is_nsfw_content = await is_nsfw_pyrogram(client, message)
        
        if is_nsfw_content:
            try:
                await message.delete()
                
                # Get user info
                try:
                    user = await client.get_users(message.from_user.id)
                    user_name = user.first_name if user else "Unknown"
                    user_id = message.from_user.id
                except Exception:
                    user_name = "Unknown"
                    user_id = message.from_user.id
                
                # Send alert
                alert_msg = (
                    f"**NSFW DETECTED**\n\n"
                    f"[{user_name}](tg://user?id={user_id}) your message contains NSFW content. "
                    f"So, Sita deleted the message.\n\n"
                    f"**NSFW Sender:** [{user_name}](tg://user?id={user_id})\n"
                    f"**Chat:** {message.chat.title}\n\n"
                    f"`⚔️ Automatic Detections Powered By Sita AI`\n"
                    f"**#GROUP_GUARDIAN**"
                )
                
                sent_msg = await client.send_message(
                    message.chat.id,
                    alert_msg,
                    disable_web_page_preview=True
                )
                
                # Delete alert after 10 seconds
                await asyncio.sleep(10)
                try:
                    await sent_msg.delete()
                except Exception:
                    pass
            except Exception as e:
                logging.error(f"Error deleting NSFW content: {e}")
    except Exception:
        pass


"""
# Old commented code - keeping for reference
@pbot.on_message(filters.incoming & filters.media & ~filters.private & ~filters.channel & ~filters.bot)
async def nsfw_watch(client, message):
    lol = get_all_nsfw_chats()
    if len(lol) == 0:
        message.continue_propagation()
    if not is_chat_in_db(message.chat.id):
        message.continue_propagation()
    hot = await is_nsfw(client, message)
    if not hot:
        message.continue_propagation()
    else:
        try:
            await message.delete()
        except:
            pass
        lolchat = await client.get_chat(message.chat.id)
        ctitle = lolchat.title
        if lolchat.username:
            hehe = lolchat.username
        else:
            hehe = message.chat.id
        midhun = await client.get_users(message.from_user.id)
        await message.delete()
        if midhun.username:
            Escobar = midhun.username
        else:
            Escobar = midhun.id
        await client.send_message(
            message.chat.id,
            f"**NSFW DETECTED**\n\n{hehe}'s message contain NSFW content.. So, Sita deleted the message\n\n **Nsfw Sender - User / Bot :** `{Escobar}` \n**Chat Title:** `{ctitle}` \n\n`⚔️Automatic Detections Powered By SitaAI` \n**#GROUP_GUARDIAN** ",
        )
        message.continue_propagation()
"""


# This Module is ported from https://github.com/MissJuliaRobot/MissJuliaRobot
# This hardwork was completely done by MissJuliaRobot
# Full Credits goes to MissJuliaRobot


approved_users = db.approve
spammers = db.spammer
globalchat = db.globchat

CMD_STARTERS = "/"
profanity.load_censor_words_from_file("./profanity_wordlist.txt")


@register(pattern="^/profanity(?: |$)(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if not event.is_group:
        await event.reply("You Can Only profanity in Groups.")
        return
    event.pattern_match.group(1)
    if not await is_admin(event, BOT_ID):
        await event.reply("`I Should Be Admin To Do This!`")
        return
    if await is_admin(event, event.message.sender_id):
        input = event.pattern_match.group(1)
        chats = spammers.find({})
        if not input:
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply(
                        "Please provide some input yes or no.\n\nCurrent setting is : **on**"
                    )
                    return
            await event.reply(
                "Please provide some input yes or no.\n\nCurrent setting is : **off**"
            )
            return
        if input == "on":
            if event.is_group:
                chats = spammers.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        await event.reply(
                            "Profanity filter is already activated for this chat."
                        )
                        return
                spammers.insert_one({"id": event.chat_id})
                await event.reply("Profanity filter turned on for this chat.")
        if input == "off":
            if event.is_group:
                chats = spammers.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        spammers.delete_one({"id": event.chat_id})
                        await event.reply("Profanity filter turned off for this chat.")
                        return
            await event.reply("Profanity filter isn't turned on for this chat.")
        if not input == "on" and not input == "off":
            await event.reply("I only understand by on or off")
            return
    else:
        await event.reply("`You Should Be Admin To Do This!`")
        return


@register(pattern="^/globalmode(?: |$)(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if not event.is_group:
        await event.reply("You Can Only enable global mode Watch in Groups.")
        return
    event.pattern_match.group(1)
    if not await is_admin(event, BOT_ID):
        await event.reply("`I Should Be Admin To Do This!`")
        return
    if await is_admin(event, event.message.sender_id):

        input = event.pattern_match.group(1)
        chats = globalchat.find({})
        if not input:
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply(
                        "Please provide some input yes or no.\n\nCurrent setting is : **on**"
                    )
                    return
            await event.reply(
                "Please provide some input yes or no.\n\nCurrent setting is : **off**"
            )
            return
        if input == "on":
            if event.is_group:
                chats = globalchat.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        await event.reply(
                            "Global mode is already activated for this chat."
                        )
                        return
                globalchat.insert_one({"id": event.chat_id})
                await event.reply("Global mode turned on for this chat.")
        if input == "off":
            if event.is_group:
                chats = globalchat.find({})
                for c in chats:
                    if event.chat_id == c["id"]:
                        globalchat.delete_one({"id": event.chat_id})
                        await event.reply("Global mode turned off for this chat.")
                        return
            await event.reply("Global mode isn't turned on for this chat.")
        if not input == "on" and not input == "off":
            await event.reply("I only understand by on or off")
            return
    else:
        await event.reply("`You Should Be Admin To Do This!`")
        return


# Pyrogram handler for /profanity command
@pbot.on_message(filters.command("profanity") & filters.group & ~filters.bot)
async def profanity_command_pyrogram(client, message):
    """Enable/disable profanity filter"""
    try:
        if not message.chat:
            return
        
        # Check if user is admin
        try:
            user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                await message.reply_text("❗ **You need to be admin to use this command.**")
                return
        except Exception:
            await message.reply_text("❗ **You need to be admin to use this command.**")
            return
        
        if len(message.command) < 2:
            # Check current status
            chat_id = message.chat.id
            chats = spammers.find({})
            is_enabled = False
            for c in chats:
                if c.get("id") == chat_id:
                    is_enabled = True
                    break
            
            status_text = "**on**" if is_enabled else "**off**"
            await message.reply_text(
                f"**Profanity Filter Status:** {status_text}\n\n"
                f"Usage: `/profanity on` or `/profanity off`"
            )
            return
        
        input_str = message.command[1].lower()
        chat_id = message.chat.id
        
        if input_str == "on":
            chats = spammers.find({})
            for c in chats:
                if c.get("id") == chat_id:
                    await message.reply_text("✅ **Profanity filter is already enabled for this chat.**")
                    return
            spammers.insert_one({"id": chat_id})
            await message.reply_text("✅ **Profanity filter turned on for this chat.**")
        elif input_str == "off":
            chats = spammers.find({})
            found = False
            for c in chats:
                if c.get("id") == chat_id:
                    spammers.delete_one({"id": chat_id})
                    found = True
                    break
            if found:
                await message.reply_text("❌ **Profanity filter turned off for this chat.**")
            else:
                await message.reply_text("❌ **Profanity filter isn't enabled for this chat.**")
        else:
            await message.reply_text("❗ **I only understand `on` or `off`**\nUsage: `/profanity on` or `/profanity off`")
    except Exception as e:
        logging.error(f"Error in profanity command: {e}")
        await message.reply_text(f"❗ **Error:** {str(e)}")


# Pyrogram profanity filter
@pbot.on_message(filters.text & filters.group & ~filters.private & ~filters.bot, group=3)
async def profanity_filter_pyrogram(client, message):
    """Filter profanity words when profanity filter is enabled"""
    try:
        if not message.text or not message.chat:
            return
        
        # Check if profanity filter is enabled for this chat
        chat_id_str = str(message.chat.id)
        chats = spammers.find({})
        is_enabled = False
        for c in chats:
            if str(c.get("id")) == chat_id_str:
                is_enabled = True
                break
        
        if not is_enabled:
            return
        
        # Check if bot is admin
        try:
            bot_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
            if bot_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                return
        except Exception:
            return
        
        # Skip if sender is admin
        try:
            user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                return
        except Exception:
            pass
        
        # Check for profanity
        msg_text = str(message.text)
        if better_profanity.profanity.contains_profanity(msg_text):
            try:
                await message.delete()
                
                # Get user info
                try:
                    user = await client.get_users(message.from_user.id)
                    user_name = user.first_name if user else "Unknown"
                    user_id = message.from_user.id
                except Exception:
                    user_name = "Unknown"
                    user_id = message.from_user.id
                
                # Send alert message
                alert_msg = (
                    f"[{user_name}](tg://user?id={user_id}) your message **`{msg_text[:50]}...`** "
                    f"contains profanity/slang words and has been deleted.\n\n"
                    f"**Reason:** Profanity filter is enabled in this chat."
                )
                
                sent_msg = await message.reply_text(
                    alert_msg,
                    disable_web_page_preview=True
                )
                
                # Delete alert after 10 seconds
                await asyncio.sleep(10)
                try:
                    await sent_msg.delete()
                except Exception:
                    pass
            except Exception as e:
                logging.error(f"Error deleting profanity message: {e}")
    except Exception:
        pass


@tbot.on(events.NewMessage(pattern=None))
async def del_profanity(event):
    if event.is_private:
        return
    msg = str(event.text)
    sender = await event.get_sender()
    # let = sender.username
    if await is_admin(event, event.message.sender_id):
        return
    chats = spammers.find({})
    for c in chats:
        if event.text:
            if event.chat_id == c["id"]:
                if better_profanity.profanity.contains_profanity(msg):
                    await event.delete()
                    if sender.username is None:
                        st = sender.first_name
                        hh = sender.id
                        final = f"[{st}](tg://user?id={hh}) **{msg}** is detected as a slang word and your message has been deleted"
                    else:
                        final = f"Sir **{msg}** is detected as a slang word and your message has been deleted"
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()
        if event.photo:
            if event.chat_id == c["id"]:
                await event.client.download_media(event.photo, "nudes.jpg")
                if nude.is_nude("./nudes.jpg"):
                    await event.delete()
                    st = sender.first_name
                    hh = sender.id
                    final = f"**NSFW DETECTED**\n\n{st}](tg://user?id={hh}) your message contain NSFW content.. So, Sita deleted the message\n\n **Nsfw Sender - User / Bot :** {st}](tg://user?id={hh})  \n\n`⚔️Automatic Detections Powered By Sita AI` \n**#GROUP_GUARDIAN** "
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()
                    os.remove("nudes.jpg")


try:
    from emoji import EMOJI_DATA as EMOJI_MAP
except Exception:
    try:
        from emoji import UNICODE_EMOJI as EMOJI_MAP
    except Exception:
        EMOJI_MAP = {}

def extract_emojis(s):
    return "".join(c for c in s if c in EMOJI_MAP)


@tbot.on(events.NewMessage(pattern=None))
async def del_profanity(event):
    if event.is_private:
        return
    msg = str(event.text)
    sender = await event.get_sender()
    # sender.username
    if await is_admin(event, event.message.sender_id):
        return
    chats = globalchat.find({})
    for c in chats:
        if event.text:
            if event.chat_id == c["id"]:
                u = msg.split()
                emj = extract_emojis(msg)
                msg = msg.replace(emj, "")
                if (
                    [(k) for k in u if k.startswith("@")]
                    and [(k) for k in u if k.startswith("#")]
                    and [(k) for k in u if k.startswith("/")]
                    and re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []
                ):
                    h = " ".join(filter(lambda x: x[0] != "@", u))
                    km = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", h)
                    tm = km.split()
                    jm = " ".join(filter(lambda x: x[0] != "#", tm))
                    hm = jm.split()
                    rm = " ".join(filter(lambda x: x[0] != "/", hm))
                elif [(k) for k in u if k.startswith("@")]:
                    rm = " ".join(filter(lambda x: x[0] != "@", u))
                elif [(k) for k in u if k.startswith("#")]:
                    rm = " ".join(filter(lambda x: x[0] != "#", u))
                elif [(k) for k in u if k.startswith("/")]:
                    rm = " ".join(filter(lambda x: x[0] != "/", u))
                elif re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []:
                    rm = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", msg)
                else:
                    rm = msg
                # print (rm)
                b = translator.detect(rm)
                if not "en" in b and not b == "":
                    await event.delete()
                    st = sender.first_name
                    hh = sender.id
                    final = f"[{st}](tg://user?id={hh}) you should only speak in english here !"
                    dev = await event.respond(final)
                    await asyncio.sleep(10)
                    await dev.delete()
#

__help__ = """```
❖ ɢsʜɪєʟᴅ ❖```

<b> Group Guardian: </b>
✪ Layla can protect your group from NSFW senders, Slag word users and also can force members to use English

<b>Commmands</b>
 ❍ /gshield <i>on/off</i> - Enable|Disable Porn cleaning
 ❍ /globalmode <i>on/off</i> - Enable|Disable English only mode
 ❍ /profanity <i>on/off</i> - Enable|Disable slag word cleaning
 
Note: Special credits goes to Julia project and Friday Userbot
 
"""
__mod_name__ = "Shield"
