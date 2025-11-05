import os
from typing import Optional

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from sitaBot import pbot
import requests


CATBOX_URL = "https://catbox.moe/user/api.php"


def _upload_catbox(file_path: str) -> Optional[str]:
    try:
        with open(file_path, "rb") as f:
            resp = requests.post(
                CATBOX_URL,
                data={"reqtype": "fileupload", "json": "true"},
                files={"fileToUpload": f},
                timeout=120,
            )
        if resp.status_code == 200:
            return resp.text.strip()
        return None
    except Exception:
        return None


@pbot.on_message(filters.command(["tgm", "tgt", "telegraph", "tl"]))
async def tgraph_upload(_, m: Message):
    if not m.reply_to_message:
        return await m.reply_text("❖ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇᴅɪᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ɢᴇᴛ ᴀ ʟɪɴᴋ")

    media = m.reply_to_message
    size = 0
    if getattr(media, "photo", None):
        size = media.photo.file_size
    elif getattr(media, "video", None):
        size = media.video.file_size
    elif getattr(media, "document", None):
        size = media.document.file_size

    status = await m.reply_text("❍ ᴘʀᴏᴄᴇssɪɴɢ...")
    try:
        local = await media.download()
        await status.edit_text("❍ ᴜᴘʟᴏᴀᴅɪɴɢ...")
        url = _upload_catbox(local)
        if not url:
            await status.edit_text("❖ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ")
            return
        await status.edit_text(
            f"❖ | [ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ]({url}) | ❖",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("• ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ •", url=url)]]
            ),
            disable_web_page_preview=True,
        )
    finally:
        try:
            if 'local' in locals() and os.path.exists(local):
                os.remove(local)
        except Exception:
            pass


__mod_name__ = "T-Graph"
__help__ = """
❍ /tgm, /tgt, /telegraph, /tl: Reply to any media to upload and get a link.
"""


