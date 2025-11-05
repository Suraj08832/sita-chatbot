from io import BytesIO
from typing import List

from pyrogram import filters
from pyrogram.types import Message

from sitaBot import pbot

import aiohttp


API_ENDPOINT = "https://bot.lyo.su/quote/generate.png"


async def _text_or_caption(msg: Message) -> str:
    if msg.text:
        return msg.text
    if msg.caption:
        return msg.caption
    return ""


async def _entities(msg: Message) -> List[dict]:
    result: List[dict] = []
    source = msg.entities or msg.caption_entities or []
    for ent in source:
        try:
            etype = ent.type.name.lower()
        except Exception:
            etype = str(ent.type).lower()
        result.append({"type": etype, "offset": ent.offset, "length": ent.length})
    return result


async def _sender_id(msg: Message) -> int:
    if msg.from_user:
        return msg.from_user.id
    if msg.sender_chat:
        return msg.sender_chat.id
    return 1


async def _sender_name(msg: Message) -> str:
    if msg.from_user:
        if msg.from_user.last_name:
            return f"{msg.from_user.first_name} {msg.from_user.last_name}"
        return msg.from_user.first_name
    if msg.sender_chat:
        return msg.sender_chat.title or ""
    return ""


async def _sender_username(msg: Message) -> str:
    if msg.from_user and msg.from_user.username:
        return msg.from_user.username
    if msg.sender_chat and msg.sender_chat.username:
        return msg.sender_chat.username
    return ""


async def _sender_photo(msg: Message):
    u = msg.from_user
    if u and u.photo:
        return {
            "small_file_id": u.photo.small_file_id,
            "small_photo_unique_id": u.photo.small_photo_unique_id,
            "big_file_id": u.photo.big_file_id,
            "big_photo_unique_id": u.photo.big_photo_unique_id,
        }
    c = msg.sender_chat
    if c and c.photo:
        return {
            "small_file_id": c.photo.small_file_id,
            "small_photo_unique_id": c.photo.small_photo_unique_id,
            "big_file_id": c.photo.big_file_id,
            "big_photo_unique_id": c.photo.big_photo_unique_id,
        }
    return ""


async def _to_quotly_payload(messages: List[Message], include_reply: bool) -> dict:
    if not isinstance(messages, list):
        messages = [messages]
    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "messages": [],
    }
    for m in messages:
        item = {
            "entities": await _entities(m),
            "chatId": await _sender_id(m),
            "text": await _text_or_caption(m),
            "avatar": True,
            "from": {
                "id": await _sender_id(m),
                "name": await _sender_name(m),
                "username": await _sender_username(m),
                "type": m.chat.type.name.lower(),
                "photo": await _sender_photo(m),
            },
            "replyMessage": {},
        }
        if include_reply and m.reply_to_message:
            rm = m.reply_to_message
            item["replyMessage"] = {
                "name": await _sender_name(rm),
                "text": await _text_or_caption(rm),
                "chatId": await _sender_id(rm),
            }
        payload["messages"].append(item)
    return payload


@pbot.on_message(filters.command("q") & filters.reply)
async def quotly_cmd(_, m: Message):
    args = m.text.split()[1:]
    include_reply = any(a.lower() == "r" for a in args)

    # count between 1 and 10
    count = 1
    for a in args:
        if a.isdigit():
            try:
                count = max(1, min(10, int(a)))
            except Exception:
                pass

    processing = await m.reply_text("⚡")
    try:
        if count == 1:
            msgs = [m.reply_to_message]
        else:
            ids = list(range(m.reply_to_message.id, m.reply_to_message.id + count))
            fetched = await _.get_messages(chat_id=m.chat.id, message_ids=ids, replies=-1)
            msgs = [x for x in fetched if (not x.empty and not x.media)]

        payload = await _to_quotly_payload(msgs, include_reply)
        async with aiohttp.ClientSession() as session:
            async with session.post(API_ENDPOINT, json=payload) as resp:
                if resp.status != 200:
                    txt = await resp.text()
                    await processing.edit_text(f"ERROR: {resp.status} {txt}")
                    return
                data = await resp.read()
        sticker = BytesIO(data)
        sticker.name = "quote.webp"
        await m.reply_sticker(sticker)
    finally:
        try:
            await processing.delete()
        except Exception:
            pass


__mod_name__ = "Quotly"
__help__ = """
- /q [r] [1-10]: Reply to a message to create a quote sticker. Use r to include replied preview.
"""


