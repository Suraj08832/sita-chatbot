# credits @InukaAsith, @Mr_dark_prince

import asyncio
import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus

from sitaBot import DRAGONS as SUDO_USERS
from sitaBot import pbot
from sitaBot.modules.sql_extended import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
async def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        channel = chat_db.channel
        try:
            chat_member = await client.get_chat_member(chat_id, user_id)
            if chat_member.restricted_by:
                if chat_member.restricted_by.id == (await client.get_me()).id:
                    try:
                        await client.get_chat_member(channel, user_id)
                        await client.unban_chat_member(chat_id, user_id)
                        await cb.message.delete()
                    except UserNotParticipant:
                        await client.answer_callback_query(
                            cb.id,
                            text=f"❗ Join our @{channel} channel and press 'UnMute Me' button.",
                            show_alert=True,
                        )
                else:
                    await client.answer_callback_query(
                        cb.id,
                        text="❗ You have been muted by admins due to some other reason.",
                        show_alert=True,
                    )
            else:
                me = await client.get_chat_member(chat_id, (await client.get_me()).id)
                if me.status != ChatMemberStatus.ADMINISTRATOR:
                    await client.send_message(
                        chat_id,
                        f"❗ **{cb.from_user.mention} is trying to UnMute himself but i can't unmute him because i am not an admin in this chat add me as admin again.**\n__#Leaving this chat...__",
                    )
                else:
                    await client.answer_callback_query(
                        cb.id,
                        text="❗ Warning! Don't press the button when you cn talk.",
                        show_alert=True,
                    )
        except Exception as e:
            await client.answer_callback_query(cb.id, text=f"Error: {str(e)}", show_alert=True)


@pbot.on_message(filters.text & ~filters.private, group=1)
async def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        user_id = message.from_user.id
        try:
            user_member = await client.get_chat_member(chat_id, user_id)
            if (
                user_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
                and user_id not in SUDO_USERS
            ):
                channel = chat_db.channel
                try:
                    await client.get_chat_member(channel, user_id)
                except UserNotParticipant:
                    try:
                        sent_message = await message.reply_text(
                            "Welcome {} 🙏 \n **You havent joined our @{} Channel yet** 😭 \n \nPlease Join [Our Channel](https://t.me/{}) and hit the **UNMUTE ME** Button. \n \n ".format(
                                message.from_user.mention, channel, channel
                            ),
                            disable_web_page_preview=True,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton(
                                            "Join Channel",
                                            url="https://t.me/{}".format(channel),
                                        )
                                    ],
                                    [
                                        InlineKeyboardButton(
                                            "UnMute Me", callback_data="onUnMuteRequest"
                                        )
                                    ],
                                ]
                            ),
                        )
                        await client.restrict_chat_member(
                            chat_id, user_id, ChatPermissions(can_send_messages=False)
                        )
                    except ChatAdminRequired:
                        try:
                            await sent_message.edit(
                                "❗ **Bot is not admin here..**\n__Give me ban permissions and retry.. \n#Ending FSub...__"
                            )
                        except:
                            pass

                except ChatAdminRequired:
                    await client.send_message(
                        chat_id,
                        text=f"❗ **I not an admin of @{channel} channel.**\n__Give me admin of that channel and retry.\n#Ending FSub...__",
                    )
        except Exception:
            pass


@pbot.on_message(filters.command(["forcesubscribe", "fsub"]) & filters.group & ~filters.bot)
async def config(client, message):
    try:
        # Check if message has chat
        if not message.chat:
            return
        
        # Get user info
        try:
            user = await client.get_chat_member(message.chat.id, message.from_user.id)
            status = getattr(user, "status", None)
            is_owner = status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
            user_id = user.user.id if hasattr(user, 'user') else getattr(user, 'user_id', message.from_user.id)
            
            # Check if user is owner or admin or sudo
            if not (is_owner or user_id in SUDO_USERS):
                await message.reply_text(
                    "❗ **Permission Denied**\n__You need to be group creator or admin to use this command.__"
                )
                return
        except Exception as e:
            logging.error(f"Error checking user permissions: {e}")
            await message.reply_text(f"Error checking permissions: {str(e)}")
            return
        
        chat_id = message.chat.id
        
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "").strip()
            
            if not input_str:
                await message.reply_text("❗ **Please provide a channel username.**\nUsage: `/fsub @channel_username`")
                return
            
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                await message.reply_text("❌ **Force Subscribe is Disabled Successfully.**")
            elif input_str.lower() in ("clear",):
                sent_message = await message.reply_text(
                    "**Unmuting all members who are muted by me...**"
                )
                try:
                    unmuted_count = 0
                    me_obj = await client.get_me()
                    async for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by and chat_member.restricted_by.id == me_obj.id:
                            try:
                                await client.unban_chat_member(chat_id, chat_member.user.id)
                                unmuted_count += 1
                                await asyncio.sleep(0.5)
                            except Exception:
                                pass
                    await sent_message.edit(f"✅ **UnMuted {unmuted_count} member(s) who were muted by me.**")
                except ChatAdminRequired:
                    await sent_message.edit(
                        "❗ **I am not an admin in this chat.**\n__I can't unmute members because i am not an admin in this chat make me admin with ban user permission.__"
                    )
                except Exception as e:
                    await sent_message.edit(f"❗ **Error:** {str(e)}")
            else:
                # Add channel
                try:
                    # Check if bot is admin in the channel
                    channel_username = input_str
                    try:
                        bot_member = await client.get_chat_member(channel_username, "me")
                        if bot_member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                            await message.reply_text(
                                f"❗ **Not an Admin in the Channel**\n__I am not an admin in the [channel](https://t.me/{channel_username}). Add me as an admin in order to enable ForceSubscribe.__",
                                disable_web_page_preview=True,
                            )
                            return
                    except UserNotParticipant:
                        await message.reply_text(
                            f"❗ **Not an Admin in the Channel**\n__I am not an admin in the [channel](https://t.me/{channel_username}). Add me as an admin in order to enable ForceSubscribe.__",
                            disable_web_page_preview=True,
                        )
                        return
                    
                    # Add channel to database
                    sql.add_channel(chat_id, channel_username)
                    await message.reply_text(
                        f"✅ **Force Subscribe is Enabled**\n__Force Subscribe is enabled, all the group members have to subscribe this [channel](https://t.me/{channel_username}) in order to send messages in this group.__",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    await message.reply_text(f"❗ **Invalid Channel Username:** `{input_str}`\n__Please provide a valid channel username without @.__")
                except Exception as err:
                    logging.error(f"Error setting up fsub: {err}")
                    await message.reply_text(f"❗ **ERROR:** `{str(err)}`")
        else:
            # Show current settings
            if sql.fs_settings(chat_id):
                channel = sql.fs_settings(chat_id).channel
                await message.reply_text(
                    f"✅ **Force Subscribe is enabled in this chat.**\n__For this [Channel](https://t.me/{channel})__\n\nUse `/fsub disable` to turn off.\nUse `/fsub clear` to unmute all muted members.",
                    disable_web_page_preview=True,
                )
            else:
                await message.reply_text(
                    "❌ **Force Subscribe is disabled in this chat.**\n\nUse `/fsub @channel_username` to enable."
                )
    except Exception as e:
        logging.error(f"Error in fsub command: {e}", exc_info=True)
        try:
            await message.reply_text(f"❗ **Error:** `{str(e)}`")
        except Exception:
            pass


__help__ = """```
❖ F-SUB ❖```

*Force Subscribe:*
❍ Sita can mute members who are not subscribed your channel until they subscribe
❍ When enabled I will mute unsubscribed members and show them a unmute button. When they pressed the button I will unmute them
*Setup*
*Only creator*
❍ Add me in your group as admin
❍ Add me in your channel as admin 
 
*Commmands*
 ❍ /fsub {channel username} - To turn on and setup the channel.
  💡Do this first...
 ❍ /fsub - To get the current settings.
 ❍ /fsub disable - To turn of ForceSubscribe..
  💡If you disable fsub, you need to set again for working.. /fsub {channel username} 
 ❍ /fsub clear - To unmute all members who muted by me.
"""
__mod_name__ = "F-Sub"
