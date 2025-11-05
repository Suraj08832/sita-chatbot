from pyrogram.enums import ParseMode

from sitaBot import EVENT_LOGS, pbot


async def send_event_log(text: str) -> None:
    """Send a log message to EVENT_LOGS (if configured).

    - Uses Pyrogram client so it works for pyrogram-powered features.
    - Silently ignores failures or missing configuration.
    """
    try:
        if not EVENT_LOGS:
            return
        await pbot.send_message(
            chat_id=str(EVENT_LOGS),
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        # best-effort logging; ignore errors
        pass


