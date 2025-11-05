# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import UserNotParticipant

from sitaBot import pbot
from sitaBot.utils.pyro_logger import send_event_log


# Runtime state: keep track of chats currently tagging to allow stop
_active_tag_chats = []  # list of chat_ids

EMOJI = [
    "🦋🦋🦋🦋🦋",
    "🧚🌸🧋🍬🫖",
    "🥀🌷🌹🌺💐",
    "🌸🌿💮🌱🌵",
    "❤️💚💙💜🖤",
    "💓💕💞💗💖",
    "🌸💐🌺🌹🦋",
    "🍔🦪🍛🍲🥗",
    "🍎🍓🍒🍑🌶️",
    "🧋🥤🧋🥛🍷",
    "🍬🍭🧁🎂🍡",
    "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚",
    "🫖☕🍹🍷🥛",
    "☕🧃🍩🍦🍙",
    "🍁🌾💮🍂🌿",
    "🌨️🌥️⛈️🌩️🌧️",
    "🌷🏵️🌸🌺💐",
    "💮🌼🌻🍀🍁",
    "🧟🦸🦹🧙👸",
    "🧅🍠🥕🌽🥦",
    "🐷🐹🐭🐨🐻‍❄️",
    "🦋🐇🐀🐈🐈‍⬛",
    "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇",
    "🍴🍽️🔪🍶🥃",
    "🕌🏰🏩⛩️🏩",
    "🎉🎊🎈🎂🎀",
    "🪴🌵🌴🌳🌲",
    "🎄🎋🎍🎑🎎",
    "🦅🦜🕊️🦤🦢",
    "🦤🦩🦚🦃🦆",
    "🐬🦭🦈🐋🐳",
    "🐔🐟🐠🐡🦐",
    "🦩🦀🦑🐙🦪",
    "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨",
    "🥬🍉🧁🧇",
]

TAG_LINES = [
    " ** ʜᴇʏ ʙᴀʙʏ ᴋᴀʜᴀ ʜᴏ 🤗** ",
    " ** ᴏʏᴇ sᴏ ɢʏᴇ ᴋʏᴀ ᴏɴʟɪɴᴇ ᴀᴀᴏ 😊** ",
    " ** ᴠᴄ ᴄʜᴀʟᴏ ʙᴀᴛᴇɴ ᴋᴀʀᴛᴇ ʜᴀɪɴ ᴋᴜᴄʜ ᴋᴜᴄʜ 😃** ",
    " ** ᴋʜᴀɴᴀ ᴋʜᴀ ʟɪʏᴇ ᴊɪ..?? 🥲** ",
    " ** ɢʜᴀʀ ᴍᴇ sᴀʙ ᴋᴀɪsᴇ ʜᴀɪɴ ᴊɪ 🥺** ",
    " ** ᴘᴛᴀ ʜᴀɪ ʙᴏʜᴏᴛ ᴍɪss ᴋᴀʀ ʀʜɪ ᴛʜɪ ᴀᴀᴘᴋᴏ 🤭** ",
    " ** ᴏʏᴇ ʜᴀʟ ᴄʜᴀʟ ᴋᴇsᴀ ʜᴀɪ..?? 🤨** ",
    " ** ᴍᴇʀɪ ʙʜɪ sᴇᴛᴛɪɴɢ ᴋᴀʀʙᴀ ᴅᴏɢᴇ..?? 🙂** ",
    " ** ᴀᴀᴘᴋᴀ ɴᴀᴍᴇ ᴋʏᴀ ʜᴀɪ..?? 🥲** ",
    " ** ɴᴀsᴛᴀ ʜᴜᴀ ᴀᴀᴘᴋᴀ..?? 😋** ",
    " ** ᴍᴇʀᴇ ᴋᴏ ᴀᴘɴᴇ ɢʀᴏᴜᴘ ᴍᴇ ᴋɪᴅɴᴀᴘ ᴋʀ ʟᴏ 😍** ",
    " ** ᴀᴀᴘᴋɪ ᴘᴀʀᴛɴᴇʀ ᴀᴀᴘᴋᴏ ᴅʜᴜɴᴅ ʀʜᴇ ʜᴀɪɴ ᴊʟᴅɪ ᴏɴʟɪɴᴇ ᴀʏɪᴀᴇ 😅** ",
    " ** ᴍᴇʀᴇ sᴇ ᴅᴏsᴛɪ ᴋʀᴏɢᴇ..?? 🤔** ",
    " ** ᴇᴅʜᴀʀ ᴅᴇᴋʜᴏ ᴋʏᴀ ʜᴀɪ @about_brahix ...😘** ",
    " ** ʙᴀʙᴜ ʏᴇ ᴅᴇᴋʜᴏ ᴀʟᴘʜᴀ ᴋᴀ ᴀᴅᴅᴀ @Oye_Careless... 😎** ",
    " ** sᴏɴᴇ ᴄʜᴀʟ ɢʏᴇ ᴋʏᴀ 🙄** ",
    " ** ᴇᴋ sᴏɴɢ ᴘʟᴀʏ ᴋʀᴏ ɴᴀ ᴘʟss 😕** ",
    " ** ᴀᴀᴘ ᴋᴀʜᴀ sᴇ ʜᴏ..?? 🙃** ",
    " ** ʜᴇʟʟᴏ ᴊɪ ɴᴀᴍᴀsᴛᴇ 😛** ",
    " ** ʜᴇʟʟᴏ ʙᴀʙʏ ᴋᴋʀʜ..? 🤔** ",
    " ** ᴅᴏ ʏᴏᴜ ᴋɴᴏᴡ ᴡʜᴏ ɪs ᴍʏ ᴏᴡɴᴇʀ.? ☺️** ",
    " ** ᴄʜʟᴏ ᴋᴜᴄʜ ɢᴀᴍᴇ ᴋʜᴇʟᴛᴇ ʜᴀɪɴ.🤗** ",
    " ** ᴀᴜʀ ʙᴀᴛᴀᴏ ᴋᴀɪsᴇ ʜᴏ ʙᴀʙʏ 😇** ",
    " ** ᴛᴜᴍʜᴀʀɪ ᴍᴜᴍᴍʏ ᴋʏᴀ ᴋᴀʀ ʀᴀʜɪ ʜᴀɪ 🤭** ",
    " ** ᴍᴇʀᴇ sᴇ ʙᴀᴛ ɴᴏɪ ᴋʀᴏɢᴇ 🥺** ",
    " ** ᴏʏᴇ ᴘᴀɢᴀʟ ᴏɴʟɪɴᴇ ᴀᴀ ᴊᴀ 😶** ",
    " ** ᴀᴀᴊ ʜᴏʟɪᴅᴀʏ ʜᴀɪ ᴋʏᴀ sᴄʜᴏᴏʟ ᴍᴇ..?? 🤔** ",
    " ** ᴏʏᴇ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 😜** ",
    " ** sᴜɴᴏ ᴇᴋ ᴋᴀᴍ ʜᴀɪ ᴛᴜᴍsᴇ 🙂** ",
    " ** ᴋᴏɪ sᴏɴɢ ᴘʟᴀʏ ᴋʀᴏ ɴᴀ 😪** ",
    " ** ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ᴜʜ ☺** ",
    " ** ᴍᴇʀᴀ ʙᴀʙᴜ ɴᴇ ᴛʜᴀɴᴀ ᴋʜᴀʏᴀ ᴋʏᴀ..? 🙊** ",
    " ** sᴛᴜᴅʏ ᴄᴏᴍᴘʟᴇᴛᴇ ʜᴜᴀ?? 😺** ",
    " ** ʙᴏʟᴏ ɴᴀ ᴋᴜᴄʜ ʏʀʀ 🥲** ",
    " ** sᴏɴᴀʟɪ ᴋᴏɴ ʜᴀɪ...?? 😅** ",
    " ** ᴛᴜᴍʜᴀʀɪ ᴇᴋ ᴘɪᴄ ᴍɪʟᴇɢɪ..? 😅** ",
    " ** ᴍᴜᴍᴍʏ ᴀᴀ ɢʏɪ ᴋʏᴀ 😆** ",
    " ** ᴏʀ ʙᴀᴛᴀᴏ ʙʜᴀʙʜɪ ᴋᴀɪsɪ ʜᴀɪ 😉** ",
    " ** ɪ ʟᴏᴠᴇ ʏᴏᴜ 💚** ",
    " ** ᴅᴏ ʏᴏᴜ ʟᴏᴠᴇ ᴍᴇ..? 👀** ",
    " ** ʀᴀᴋʜɪ ᴋᴀʙ ʙᴀɴᴅ ʀᴀʜɪ ʜᴏ..?? 🙉** ",
    " ** ᴇᴋ sᴏɴɢ sᴜɴᴀᴜ..? 😹** ",
    " ** ᴏɴʟɪɴᴇ ᴀᴀ ᴊᴀ ʀᴇ sᴏɴɢ sᴜɴᴀ ʀᴀʜɪ ʜᴜ 😻** ",
    " ** ɪɴsᴛᴀɢʀᴀᴍ ᴄʜᴀʟᴀᴛᴇ ʜᴏ..?? 🙃** ",
    " ** ᴡʜᴀᴛsᴀᴘᴘ ɴᴜᴍʙᴇʀ ᴅᴏɢᴇ ᴀᴘɴᴀ ᴛᴜᴍ..? 😕** ",
    " ** ᴛᴜᴍʜᴇ ᴋᴏɴ sᴀ ᴍᴜsɪᴄ sᴜɴɴᴀ ᴘᴀsᴀɴᴅ ʜᴀɪ..? 🙃** ",
    " ** sᴀʀᴀ ᴋᴀᴍ ᴋʜᴀᴛᴀᴍ ʜᴏ ɢʏᴀ ᴀᴀᴘᴋᴀ..? 🙃** ",
    " ** ᴋᴀʜᴀ sᴇ ʜᴏ ᴀᴀᴘ 😊** ",
    " ** sᴜɴᴏ ɴᴀ 🧐** ",
    " ** ᴍᴇʀᴀ ᴇᴋ ᴋᴀᴀᴍ ᴋᴀʀ ᴅᴏɢᴇ..? ♥️** ",
    " ** ʙʏ ᴛᴀᴛᴀ ᴍᴀᴛ ʙᴀᴀᴛ ᴋᴀʀɴᴀ ᴀᴀᴊ ᴋᴇ ʙᴀᴅ 😠** ",
    " ** ᴍᴏᴍ ᴅᴀᴅ ᴋᴀɪsᴇ ʜᴀɪɴ..? ❤** ",
    " ** ᴋʏᴀ ʜᴜᴀ..? 🤔** ",
    " ** ʙᴏʜᴏᴛ ʏᴀᴀᴅ ᴀᴀ ʀʜɪ ʜᴀɪ 😒** ",
    " ** ʙʜᴜʟ ɢʏᴇ ᴍᴜᴊʜᴇ 😏** ",
    " ** ᴊᴜᴛʜ ɴʜɪ ʙᴏʟɴᴀ ᴄʜᴀʜɪʏᴇ 🤐** ",
    " ** ᴋʜᴀ ʟᴏ ʙʜᴀᴡ ᴍᴀᴛ ᴋʀᴏ ʙᴀᴀᴛ 😒** ",
    " ** ᴋʏᴀ ʜᴜᴀ 😮** ",
    " ** ʜɪɪ ʜᴏɪ ʜᴇʟʟᴏ 👀** ",
    " ** ᴀᴀᴘᴋᴇ ᴊᴀɪsᴀ ᴅᴏsᴛ ʜᴏ sᴀᴛʜ ᴍᴇ ғɪʀ ɢᴜᴍ ᴋɪs ʙᴀᴀᴛ ᴋᴀ 🙈** ",
    " ** ᴀᴀᴊ ᴍᴇ sᴀᴅ ʜᴏᴏɴ ☹️** ",
    " ** ᴍᴜsᴊʜsᴇ ʙʜɪ ʙᴀᴀᴛ ᴋᴀʀ ʟᴏ ɴᴀ 🥺** ",
    " ** ᴋʏᴀ ᴋᴀʀ ʀᴀʜᴇ ʜᴏ 👀** ",
    " ** ᴋʏᴀ ʜᴀʟ ᴄʜᴀʟ ʜᴀɪ 🙂** ",
    " ** ᴋᴀʜᴀ sᴇ ʜᴏ ᴀᴀᴘ..?🤔** ",
    " ** ᴄʜᴀᴛᴛɪɴɢ ᴋᴀʀ ʟᴏ ɴᴀ..🥺** ",
    " ** ᴍᴇ ᴍᴀsᴏᴏᴍ ʜᴜ ɴᴀ 🥺** ",
    " ** ᴋᴀʟ ᴍᴀᴊᴀ ᴀʏᴀ ᴛʜᴀ ɴᴀ 😅** ",
    " ** ɢʀᴏᴜᴘ ᴍᴇ ʙᴀᴀᴛ ᴋʏᴜ ɴᴀʜɪ ᴋᴀʀᴛᴇ ʜᴏ 😕** ",
    " ** ᴀᴀᴘ ʀᴇʟᴀᴛɪᴏɴsʜɪᴘ ᴍᴇ ʜᴏ..? 👀** ",
    " ** ᴋɪᴛɴᴀ ᴄʜᴜᴘ ʀᴀʜᴛᴇ ʜᴏ ʏʀʀ 😼** ",
    " ** ᴀᴀᴘᴋᴏ ɢᴀɴᴀ ɢᴀɴᴇ ᴀᴀᴛᴀ ʜᴀɪ..? 😸** ",
    " ** ɢʜᴜᴍɴᴇ ᴄʜᴀʟᴏɢᴇ..?? 🙈** ",
    " ** ᴋʜᴜs ʀᴀʜᴀ ᴋᴀʀᴏ 🤞** ",
    " ** ʜᴀᴍ ᴅᴏsᴛ ʙᴀɴ sᴀᴋᴛᴇ ʜᴀɪ...? 🥰** ",
    " ** ᴋᴜᴄʜ ʙᴏʟ ᴋʏᴜ ɴʜɪ ʀᴀʜᴇ ʜᴏ.. 🥺** ",
    " ** ᴋᴜᴄʜ ᴍᴇᴍʙᴇʀs ᴀᴅᴅ ᴋᴀʀ ᴅᴏ 🥲** ",
    " ** sɪɴɢʟᴇ ʜᴏ ʏᴀ ᴍɪɴɢʟᴇ 😉** ",
    " ** ᴀᴀᴏ ᴘᴀʀᴛʏ ᴋᴀʀᴛᴇ ʜᴀɪɴ 🥳** ",
    " ** ʙɪᴏ ᴍᴇ ʟɪɴᴋ ʜᴀɪ ᴊᴏɪɴ ᴋᴀʀ ʟᴏ 🧐** ",
    " ** ᴍᴜᴊʜᴇ ʙʜᴜʟ ɢʏᴇ ᴋʏᴀ 🥺** ",
    " ** ʏᴀʜᴀ ᴀᴀ ᴊᴀᴏ @ALPHA_SAYS ᴍᴀsᴛɪ ᴋᴀʀᴇɴɢᴇ 🤭** ",
    " ** ᴛʀᴜᴛʜ ᴀɴᴅ ᴅᴀʀᴇ ᴋʜᴇʟᴏɢᴇ..? 😊** ",
    " ** ᴀᴀᴊ ᴍᴜᴍᴍʏ ɴᴇ ᴅᴀᴛᴀ ʏʀʀ 🥺** ",
    " ** ᴊᴏɪɴ ᴋᴀʀ ʟᴏ @brahix_support 🤗** ",
    " ** ᴇᴋ ᴅɪʟ ʜᴀɪ ᴇᴋ ᴅɪʟ ʜɪ ᴛᴏ ʜᴀɪ 😗** ",
    " ** ᴛᴜᴍʜᴀʀᴇ ᴅᴏsᴛ ᴋᴀʜᴀ ɢʏᴇ 🥺** ",
    " ** ᴍʏ ᴄᴜᴛᴇ ᴏᴡɴᴇʀ @PurviBots 🥰** ",
    " ** ᴋᴀʜᴀ ᴋʜᴏʏᴇ ʜᴏ ᴊᴀᴀɴ 😜** ",
    " ** ɢᴏᴏᴅ ɴɪɢʜᴛ ᴊɪ ʙʜᴜᴛ ʀᴀᴛ ʜᴏ ɢʏɪ 🥰** ",
]


async def _is_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
    except UserNotParticipant:
        return False
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


@pbot.on_message(filters.command(["rtag", "tagall"], prefixes=["/", "@", "#"]))
async def rtag_command(client, message):
    chat = message.chat
    if chat.type == ChatType.PRIVATE:
        return await message.reply("⬤ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs.")

    if not await _is_admin(client, chat.id, message.from_user.id):
        return await message.reply("⬤ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ, ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴛᴀɢ.")

    if chat.id in _active_tag_chats:
        return await message.reply("⬤ ᴀ ᴛᴀɢ sᴇssɪᴏɴ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ.")

    # Determine mode: reply-based or simple text line
    mode_reply = bool(message.reply_to_message)
    source_msg = message.reply_to_message if mode_reply else None

    _active_tag_chats.append(chat.id)
    await send_event_log(
        f"<b>❖ Tag Session Started</b>\n\n"
        f"<b>• Chat:</b> {chat.title or chat.id} (<code>{chat.id}</code>)\n"
        f"<b>• By:</b> {message.from_user.mention} (<code>{message.from_user.id}</code>)\n"
        f"<b>• Mode:</b> {'reply' if mode_reply else 'text'}"
    )

    try:
        async for member in client.get_chat_members(chat.id):
            if chat.id not in _active_tag_chats:
                break
            if member.user.is_bot:
                continue

            if mode_reply:
                # Reply mode: reply to source message with emoji mention
                await source_msg.reply(f"[{random.choice(EMOJI)}](tg://user?id={member.user.id})")
            else:
                # Text mode: send message with mention and tag line
                mention = f"[{member.user.first_name}](tg://user?id={member.user.id}) "
                text = f"{mention} {random.choice(TAG_LINES)}"
                await client.send_message(chat.id, text)
            
            await asyncio.sleep(4)
    finally:
        if chat.id in _active_tag_chats:
            _active_tag_chats.remove(chat.id)
        await send_event_log(
            f"<b>❖ Tag Session Ended</b>\n\n"
            f"<b>• Chat:</b> {chat.title or chat.id} (<code>{chat.id}</code>)\n"
            f"<b>• By:</b> {message.from_user.mention} (<code>{message.from_user.id}</code>)"
        )


@pbot.on_message(filters.command(["vctag"], prefixes=["/", "@", "#"]))
async def vctag_command(client, message):
    chat = message.chat
    if chat.type == ChatType.PRIVATE:
        return await message.reply("⬤ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs.")
    if not await _is_admin(client, chat.id, message.from_user.id):
        return await message.reply("⬤ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ, ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴛᴀɢ.")
    if chat.id in _active_tag_chats:
        return await message.reply("⬤ ᴀ ᴛᴀɢ sᴇssɪᴏɴ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ.")

    _active_tag_chats.append(chat.id)
    
    try:
        async for member in client.get_chat_members(chat.id):
            if chat.id not in _active_tag_chats:
                break
            if member.user.is_bot:
                continue
            
            mention = f"[{member.user.first_name}](tg://user?id={member.user.id}) "
            text = f"{mention} {random.choice(EMOJI)}"
            await client.send_message(chat.id, text)
            await asyncio.sleep(4)
    finally:
        if chat.id in _active_tag_chats:
            _active_tag_chats.remove(chat.id)


@pbot.on_message(filters.command(["rstop", "tagstop", "vcstop", "tagoff"]))
async def stop_tagging(client, message):
    chat = message.chat
    if chat.id not in _active_tag_chats:
        return await message.reply("⬤ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀɢ sᴇssɪᴏɴ.")
    if not await _is_admin(client, chat.id, message.from_user.id):
        return await message.reply("⬤ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴛᴏᴘ ᴛᴀɢɢɪɴɢ.")
    try:
        _active_tag_chats.remove(chat.id)
    except ValueError:
        pass
    await send_event_log(
        f"<b>❖ Tag Session Stopped</b>\n\n"
        f"<b>• Chat:</b> {chat.title or chat.id} (<code>{chat.id}</code>)\n"
        f"<b>• By:</b> {message.from_user.mention} (<code>{message.from_user.id}</code>)"
    )
    return await message.reply("♥︎ ᴛᴀɢ sᴛᴏᴘᴘᴇᴅ.")


__mod_name__ = "Tagall"
__help__ = """
- /tagall or /rtag: Mention all members (reply to a message to tag with emojis)
- /vctag: Mention all with VC-style lines
- /rstop: Stop an ongoing tag session (aliases: /tagstop, /vcstop, /tagoff)
"""