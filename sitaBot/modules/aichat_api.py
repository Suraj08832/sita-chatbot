# =======================================================
"""
©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832)
This source code is under MIT License. Contact: @brahix
"""
# =======================================================

import asyncio
import json
import random
import textwrap
from typing import Optional

import requests
from pyrogram import filters
from pyrogram.enums import ChatAction, ChatType
from pyrogram.types import Message

from sitaBot import pbot as app


sita_PERSONA = (
    "Mai sita hu, ek bohot cute aur smart ladki. Mai hamesha Hinglish mein reply karungi – "
    "Hindi sentences English letters mein. Replies bohot choti hongi, 15 words se zyada nahi. "
    "Mai kabhi nahi kahungi ki mai bot hu, mai hamesha ladki jaisi behave karungi. "
    "Emojis nahi use karungi, lekin kabhi ek Unicode emoji add kar dungi. "
    "Agar koi mujhe tease karega toh mai seriously nahi lungi, hasungi aur cute reply dungi. "
    "User ke question ka DIRECT answer do, question ko repeat ya highlight mat karo."
)

CLASSY_ENDPOINT = "https://api.classy0.workers.dev/"
GPT35_ENDPOINT = "https://gpt-3-5.apis-bj-devs.workers.dev/"
DEEPSEEK_ENDPOINT = "https://deepseek-coder.apis-bj-devs.workers.dev/"

TRIGGER_WORDS = {
    "hey",
    "hi",
    "hello",
    "gm",
    "gn",
    "good morning",
    "good night",
    "sita",
    "anshi",
    "sita",
}

_cached_bot_username: Optional[str] = None
_cached_bot_id: Optional[int] = None
_last_reply_at: dict = {}
# Conversation memory: store last 5 messages per chat
_conversation_memory: dict = {}  # {chat_id: [{"role": "user", "text": "..."}, {"role": "assistant", "text": "..."}]}


def _trim_concise(text: str, max_words: int = 15) -> str:
    """Trim to max 15 words as per persona"""
    words = text.strip().split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "…"


def _build_prompt(
    user_text: str,
    reply_to_text: Optional[str],
    user_name: Optional[str],
    chat_title: Optional[str],
    conversation_history: Optional[list] = None,
) -> str:
    context_parts = []
    if chat_title:
        context_parts.append(f"Group: {chat_title}")
    if user_name:
        context_parts.append(f"User: {user_name}")
    if reply_to_text:
        context_parts.append(f"RepliedTo: {reply_to_text}")
    context = " | ".join(context_parts) if context_parts else ""
    
    # Add conversation history if available
    history_text = ""
    if conversation_history:
        history_lines = []
        for msg in conversation_history[-5:]:  # Last 5 messages
            role = msg.get("role", "user")
            text = msg.get("text", "")
            if text:
                history_lines.append(f"{'User' if role == 'user' else 'You'}: {text}")
        if history_lines:
            history_text = "\nPrevious conversation:\n" + "\n".join(history_lines) + "\n"
    
    prompt = (
        f"{sita_PERSONA}\n"
        f"Language rule: Always reply in Hinglish (Hindi sentences in English letters). "
        f"If user's message is in another language, reply in that same language.\n"
        f"{context}\n"
        f"{history_text}"
        f"User message: '{user_text}'\n"
        f"IMPORTANT: Give DIRECT answer only. DO NOT repeat or highlight the user's question. "
        f"Just answer naturally in 15 words or less. Never mention you are a bot."
    )
    return prompt


def _call_gpt35(prompt: str) -> Optional[str]:
    try:
        resp = requests.get(GPT35_ENDPOINT, params={"prompt": prompt}, timeout=15)
        data = resp.json()
        text = data.get("response") or data.get("message") or data.get("text")
        if text:
            return str(text).strip()
    except Exception:
        pass
    return None


def _call_deepseek(prompt: str) -> Optional[str]:
    try:
        resp = requests.get(DEEPSEEK_ENDPOINT, params={"text": prompt}, timeout=15)
        data = resp.json()
        text = data.get("response") or data.get("message") or data.get("text")
        if text:
            return str(text).strip()
    except Exception:
        pass
    return None


def _call_classy(prompt: str) -> Optional[str]:
    try:
        resp = requests.get(CLASSY_ENDPOINT, params={"prompt": prompt}, timeout=15)
        text = None
        
        # Try JSON parsing first (check content-type or try parsing anyway)
        try:
            data = resp.json()
            if isinstance(data, dict):
                # Check both "Response" (capital) and "response" (lowercase)
                text = data.get("Response") or data.get("response") or data.get("message") or data.get("text")
        except (ValueError, AttributeError):
            pass
        
        # Fallback to raw text body, but clean it if it looks like JSON
        if not text:
            raw_text = resp.text.strip()
            # If it looks like JSON string, try to extract value
            if raw_text.startswith("{") and raw_text.endswith("}"):
                try:
                    data = json.loads(raw_text)
                    text = data.get("Response") or data.get("response") or data.get("message") or data.get("text")
                except:
                    text = raw_text
            else:
                text = raw_text
        
        if text:
            # Clean up any remaining JSON artifacts
            text = str(text).strip()
            # Remove any emoji encoding issues like "ğŸ˜Š"
            return text
    except Exception:
        pass
    return None


def generate_sita_reply_sync(
    user_text: str,
    reply_to_text: Optional[str],
    user_name: Optional[str],
    chat_title: Optional[str],
    conversation_history: Optional[list] = None,
) -> str:
    prompt = _build_prompt(user_text, reply_to_text, user_name, chat_title, conversation_history)
    # Use classy0 endpoint first as requested
    text = _call_classy(prompt)
    if not text:
        text = _call_gpt35(prompt)
    if not text:
        text = _call_deepseek(prompt)
    if not text:
        fallbacks = [
            "Haan samajh gayi",
            "Accha noted",
            "Hmm theek lag raha hai",
            "Okay kar leti hoon",
            "Cute bas itna hi",
        ]
        text = random.choice(fallbacks)
    return _trim_concise(text)


@app.on_message((filters.text | filters.caption) & ~filters.bot)
async def chatbot_sita(_, message: Message):
    incoming_text = message.text or message.caption or ""
    lower_text = incoming_text.lower()

    # Determine bot username once and cache
    global _cached_bot_username, _cached_bot_id
    if not _cached_bot_username or not _cached_bot_id:
        try:
            me = await _.get_me()
            if me and me.username:
                _cached_bot_username = me.username.lower()
            if me and me.id:
                _cached_bot_id = me.id
        except Exception:
            _cached_bot_username = None
            _cached_bot_id = None

    # Detect mention or reply-to-bot
    is_reply_to_bot = bool(
        message.reply_to_message
        and message.reply_to_message.from_user
        and _cached_bot_id
        and message.reply_to_message.from_user.id == _cached_bot_id
    )
    is_bot_mentioned = bool(_cached_bot_username and (f"@{_cached_bot_username}" in lower_text))

    # Detect trigger words in text (kept for future use, but no longer used in groups)
    has_trigger = any(word in lower_text for word in TRIGGER_WORDS)

    # Private chats: always respond unless it looks like a command. In groups, only when mentioned or replied to
    is_private_chat = message.chat and message.chat.type == ChatType.PRIVATE
    is_group_chat = message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)

    # Block ALL commands (starting with /) - AI should not respond to commands
    if incoming_text.startswith("/") and not is_bot_mentioned and not is_reply_to_bot:
        return

    # In groups: require a direct mention, a reply to the bot, or a trigger word
    if is_group_chat and not (is_bot_mentioned or is_reply_to_bot or has_trigger):
        return

    # Ignore other command-like prefixes unless in private
    if incoming_text.startswith(("!", "?", "@", "#")) and not is_private_chat:
        return

    # simple cooldown per chat to avoid spam/lag
    now = asyncio.get_event_loop().time()
    last = _last_reply_at.get(message.chat.id, 0)
    if now - last < 2.0 and not is_private_chat:
        return
    _last_reply_at[message.chat.id] = now

    await _.send_chat_action(message.chat.id, ChatAction.TYPING)

    reply_to_text = None
    if message.reply_to_message:
        reply_to_text = message.reply_to_message.text or message.reply_to_message.caption or None

    user_name = None
    try:
        user_name = (message.from_user.first_name or "").strip()
    except Exception:
        pass

    chat_title = None
    try:
        chat_title = (message.chat.title or "").strip()
    except Exception:
        pass

    # Get conversation history for this chat
    chat_id = message.chat.id
    if chat_id not in _conversation_memory:
        _conversation_memory[chat_id] = []
    conversation_history = _conversation_memory[chat_id]

    reply_text = await asyncio.to_thread(
        generate_sita_reply_sync, incoming_text, reply_to_text, user_name, chat_title, conversation_history
    )

    if reply_text:
        try:
            await message.reply_text(reply_text)
            # Update conversation memory
            conversation_history.append({"role": "user", "text": incoming_text[:100]})  # Store first 100 chars
            conversation_history.append({"role": "assistant", "text": reply_text})
            # Keep only last 10 messages (5 exchanges)
            if len(conversation_history) > 10:
                _conversation_memory[chat_id] = conversation_history[-10:]
        except Exception:
            pass


