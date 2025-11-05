# =======================================================
"""
©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832)
MIT License • DM: @brahix
"""
# =======================================================

import asyncio
import random
from math import ceil
from pyrogram import filters, enums
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, ChatMemberUpdated

from sitaBot import pbot as app, LOGGER
from sitaBot.utils.pyro_logger import send_event_log

# Ensure module is loaded
__mod_name__ = "Start"
__help__ = """
❍ /start : Start the bot and see the main menu
"""


NEXIO = [
    "https://files.catbox.moe/x5lytj.jpg",
    "https://files.catbox.moe/psya34.jpg",
    "https://files.catbox.moe/leaexg.jpg",
    "https://files.catbox.moe/b0e4vk.jpg",
    "https://files.catbox.moe/1b1wap.jpg",
    "https://files.catbox.moe/ommjjk.jpg",
    "https://files.catbox.moe/onurxm.jpg",
    "https://files.catbox.moe/97v75k.jpg",
]

PURVI_STKR = [
    "CAACAgUAAxkBAAIBO2i1Spi48ZdWCNehv-GklSI9aRYWAAJ9GAACXB-pVds_sm8brMEqHgQ",
    "CAACAgUAAxkBAAIBOmi1Sogwaoh01l5-e-lJkK1VNY6MAAIlGAACKI6wVVNEvN-6z3Z7HgQ",
]

emojis = ["🥰", "🔥", "💖", "😁", "😎", "🎉"]


def private_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("• ʜєʟᴩ & ᴄσϻϻᴧηᴅs •", callback_data="help_back"),
            ],
            [
                InlineKeyboardButton("˹ sυᴩᴩσʀᴛ ˼", url="https://t.me/brahix_support"),
                InlineKeyboardButton("˹ υᴩᴅᴧᴛєs ˼", url="https://t.me/about_brahix"),
            ],
            [
                InlineKeyboardButton("˹ ᴧʙσυᴛ ˼", callback_data="sita_"),
                InlineKeyboardButton("˹ єᴄσησϻʏ ˼", callback_data="economy_help"),
            ],
            [
                InlineKeyboardButton("➕ ᴧᴅᴅ ᴛσ ɢʀσυᴩ ➕", url="https://t.me/Sitabot?startgroup=true"),
            ],
        ]
    )


def group_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("˹ ʜєʟᴩ ˼", callback_data="help_back"),
                InlineKeyboardButton("˹ ᴄσηғɪɢ ˼", callback_data="stngs_back"),
            ]
        ]
    )


@app.on_message(filters.command(["start"]) & filters.private, group=1)
async def stylish_start_pm(_, message: Message):
    try:
        # Skip if this is a command with arguments (let telegram bot handle ghelp_, stngs_, etc)
        if len(message.command) > 1:
            args = message.command[1].lower()
            if args.startswith(("ghelp_", "stngs_", "help")):
                return  # Let telegram bot handle these
        
        try:
            await message.react(random.choice(emojis))
        except Exception:
            pass

        try:
            st = await message.reply_sticker(random.choice(PURVI_STKR))
            await asyncio.sleep(1)
            await st.delete()
        except Exception:
            pass

        # small typing animation like sequence
        try:
            purvi = await message.reply_text(f"**ʜєʟʟᴏ ᴅєᴧʀ {message.from_user.mention}**")
            await asyncio.sleep(0.4)
            await purvi.edit_text("**ɪ ᴧϻ ʏσᴜʀ ɢʀσᴜᴘ ʜєʟᴘєʀ + ғᴜɴ ʙσᴛ..**")
            await asyncio.sleep(0.4)
            await purvi.edit_text("**ʜσᴡ ᴧʀє ʏσᴜ ᴛσᴅᴧʏ?**")
            await asyncio.sleep(0.4)
            await purvi.delete()
        except Exception:
            pass

        caption = (
            "<b>✨ sɪᴛᴧ ʙσᴛ ✨</b>\n\n"
            f"<b>ʜєʟʟσ</b> {message.from_user.mention}!\n\n"
            "**ʏσυʀ ᴧʟʟ-ɪη-σηє ɢʀσυᴩ ϻᴧηᴧɢєϻєηᴛ + ғυη ʙσᴛ:**\n\n"
            "❍ ᴧᴅϻɪη ᴛσσʟs (ʙᴧη/ϻυᴛє/ᴩɪη) ⚡\n"
            "❍ ᴡᴧʀηs, ᴧηᴛɪғʟσσᴅ, ғɪʟᴛєʀs, ησᴛєs 📝\n"
            "❍ sᴛɪᴄᴋєʀ/ϻєᴅɪᴧ ᴛσσʟs, ᴛʀᴧηsʟᴧᴛσʀ, ᴡɪᴋɪ, ᴧɪ ᴄʜᴧᴛ 🎨\n"
            "❍ єᴄσησϻʏ sʏsᴛєϻ: ʀσʙ, ᴋɪʟʟ, ʟσᴛᴛєʀʏ 💰\n\n"
            "<i>❖ 𝐏ᴏᴡᴇʀᴇᴅ 𝖡ʏ » <a href=\"https://t.me/brahix\">𝆺𝅥⃝🎧×⃪͜‌ 𝐁 𝐑 𝐀 𝐇 𝐈 𝐗 ◡̈⃝⟶📻</a></i>"
        )
        sent = await message.reply_photo(
            random.choice(NEXIO),
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=private_keyboard(),
        )
        # Log PM start
        try:
            await send_event_log(
                f"<b>❖ Bot Started in PM</b>\n\n"
                f"<b>• User:</b> {message.from_user.mention} (<code>{message.from_user.id}</code>)\n"
                f"<b>• Message:</b> <code>/start</code>"
            )
        except Exception:
            pass
    except Exception as e:
        # Fallback to simple text if photo fails
        try:
            await message.reply_text(
                caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=private_keyboard(),
                disable_web_page_preview=True
            )
        except Exception:
            pass


@app.on_message(filters.command(["start"]) & filters.group, group=1)
async def stylish_start_gp(_, message: Message):
    try:
        # filters.group already covers GROUP and SUPERGROUP
        bot_me = await _.get_me()
        caption = (
            f"**{bot_me.mention}** ɪꜱ ʀᴇᴀᴅʏ ✨\n"
            f"ᴜᴘᴛɪᴍᴇ ꜱʜᴏᴡɴ ɪɴ /start ᴘᴍ. ᴜꜱᴇ ʜᴇʟᴘ ᴍᴇɴᴜ ʙᴇʟᴏᴡ."
        )
        try:
            await message.reply_photo(
                random.choice(NEXIO),
                caption=caption,
                reply_markup=group_keyboard(),
            )
        except Exception:
            await message.reply_text(
                caption,
                reply_markup=group_keyboard(),
            )
        # Log group /start
        try:
            await send_event_log(
                f"<b>❖ /start in Group</b>\n\n"
                f"<b>• Chat:</b> {message.chat.title or message.chat.id} (<code>{message.chat.id}</code>)\n"
                f"<b>• By:</b> {message.from_user.mention} (<code>{message.from_user.id}</code>)"
            )
        except Exception:
            pass
    except Exception:
        pass


def paginate_modules_pyrogram(page_n: int, module_dict: dict, prefix: str) -> list:
    """Create paginated module buttons for Pyrogram (similar to telegram bot version)"""
    modules = sorted(
        [
            InlineKeyboardButton(
                x.__mod_name__,
                callback_data=f"{prefix}_module({x.__mod_name__.lower()})"
            )
            for x in module_dict.values()
        ],
        key=lambda b: b.text
    )
    
    # Group into rows of 3
    pairs = [modules[i * 3:(i + 1) * 3] for i in range((len(modules) + 3 - 1) // 3)]
    
    round_num = len(modules) / 3
    calc = len(modules) - round(round_num)
    if calc == 1:
        pairs.append([modules[-1]])
    elif calc == 2:
        pairs.append([modules[-1]])
    
    max_num_pages = ceil(len(pairs) / 10)
    modulo_page = page_n % max_num_pages
    
    # Add pagination if needed
    if len(pairs) > 8:
        page_pairs = pairs[modulo_page * 8:8 * (modulo_page + 1)]
        page_pairs.append([
            InlineKeyboardButton("◀️ Back", callback_data=f"{prefix}_prev({modulo_page})"),
            InlineKeyboardButton("❌ Close", callback_data="sita_back"),
            InlineKeyboardButton("Next ▶️", callback_data=f"{prefix}_next({modulo_page})")
        ])
        return page_pairs
    else:
        pairs.append([InlineKeyboardButton("◀️ Back", callback_data="sita_back")])
        return pairs


@app.on_callback_query(filters.regex(r"^help_back$"))
async def cb_help(_, query: CallbackQuery):
    try:
        # Import HELPABLE and HELP_STRINGS from __main__
        try:
            from sitaBot.__main__ import HELPABLE, HELP_STRINGS
            help_text = (
                "<b>⚙️ Help Main Menu</b>\n\n"
                "• Choose a category to view commands.\n"
                "• All commands use the <code>/</code> prefix."
            )

            # Category mapping → list of module keys (lowercase)
            categories = {
                "CHAT-GPT": ["aichat_api", "aichat", "__aimultilanguage"],
                "MANAGEMENT": [
                    "admin", "bans", "muting", "locks", "blacklist", "blacklistusers",
                    "approve", "antiflood", "connection", "cust_filters", "notes",
                    "welcome", "warns", "reporting", "dbcleanup", "feds", "global_bans",
                    "disable", "__nightmode", "__forcesubs"
                ],
                "FUN": ["fun", "games", "fun_strings", "truth_and_dare", "anime", "shippering"],
                "SEARCH": ["__google", "wiki", "ud", "imdb", "gtranslator", "currency_converter", "cricketscore", "__weather", "__gps"],
                "TOOLS": ["__tools", "__encrypt", "__zip", "paste", "speed_test", "ping", "debug", "eval", "shell"],
                "INFO": ["userinfo", "gettime", "get_common_chats", "users"],
                "TAGALL": ["tagall"],
                "T-GRAPH": ["__telegraph"],
                "STICKERS": ["stickers", "blacklist_stickers", "blsticker"],
                "GITHUB": ["_pyrogithub"],
            }

            # Keep only categories that have existing modules
            available = []
            for label, mods in categories.items():
                existing = [m for m in mods if m in HELPABLE]
                if existing:
                    available.append((label, existing))

            # Build grid keyboard 3 per row
            rows = []
            temp = []
            for label, _ in available:
                temp.append(InlineKeyboardButton(label, callback_data=f"cat_{label}"))
                if len(temp) == 3:
                    rows.append(temp)
                    temp = []
            if temp:
                rows.append(temp)
            # Add an option to view the full classic list
            rows.append([InlineKeyboardButton("ALL COMMANDS", callback_data="help_all")])
            rows.append([InlineKeyboardButton("◀️ Back", callback_data="sita_back")])

            keyboard = InlineKeyboardMarkup(rows)

            # Save mapping on app object for handler access
            try:
                app.CATEGORY_MAP = {label: mods for label, mods in available}
            except Exception:
                pass
        except Exception as e:
            # Fallback if import fails
            help_text = (
                "<b>⚙️ Help & Commands</b>\n\n"
                "• Click a category below to browse commands\n"
                "• All commands use the <code>/</code> prefix\n"
                "• Need help? Join <a href=\"https://t.me/brahix_support\">support</a>"
            )
            keyboard = private_keyboard()
        
        # Check if message has photo/caption or is text
        has_photo = query.message.photo or query.message.video or query.message.document
        if has_photo:
            try:
                await query.message.edit_caption(
                    caption=help_text,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=keyboard,
                )
            except Exception:
                # If edit_caption fails, send new message
                await query.message.reply_text(
                    help_text,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )
        else:
            try:
                await query.message.edit_text(
                    help_text,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )
            except Exception:
                pass
    except Exception:
        pass
    await query.answer()


@app.on_callback_query(filters.regex(r"^help_all$"))
async def cb_help_all(_, query: CallbackQuery):
    try:
        from sitaBot.__main__ import HELPABLE
        text = (
            "<b>All Modules</b>\n"
            "Tap a module to view commands."
        )
        keyboard = InlineKeyboardMarkup(paginate_modules_pyrogram(0, HELPABLE, "help"))
        has_photo = query.message.photo or query.message.video or query.message.document
        if has_photo:
            try:
                await query.message.edit_caption(caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard)
            except Exception:
                await query.message.reply_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
        else:
            try:
                await query.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
            except Exception:
                pass
    except Exception:
        pass
    await query.answer()


@app.on_chat_member_updated()
async def log_bot_added(_, cmu: ChatMemberUpdated):
    try:
        chat = cmu.chat
        if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
            return
        # Only react to the bot's own membership updates
        me = await _.get_me()
        if not cmu.new_chat_member or not cmu.new_chat_member.user:
            return
        if cmu.new_chat_member.user.id != me.id:
            return

        new_status = cmu.new_chat_member.status
        old_status = cmu.old_chat_member.status if cmu.old_chat_member else None

        # Bot added/promoted
        if new_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR) and old_status not in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
            inviter = cmu.from_user.mention if cmu.from_user else "Unknown"
            await send_event_log(
                f"<b>❖ Bot Added to Group</b>\n\n"
                f"<b>• Chat:</b> {chat.title or chat.id} (<code>{chat.id}</code>)\n"
                f"<b>• By:</b> {inviter}\n"
                f"<b>• Status:</b> {new_status.name}"
            )
        # Bot removed/kicked
        elif new_status in (ChatMemberStatus.RESTRICTED, ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
            remover = cmu.from_user.mention if cmu.from_user else "Unknown"
            await send_event_log(
                f"<b>❖ Bot Removed from Group</b>\n\n"
                f"<b>• Chat:</b> {chat.title or chat.id} (<code>{chat.id}</code>)\n"
                f"<b>• By:</b> {remover}\n"
                f"<b>• Status:</b> {new_status.name}"
            )
    except Exception:
        pass

@app.on_callback_query(filters.regex(r"^cat_.+$"))
async def cb_category(_, query: CallbackQuery):
    try:
        from sitaBot.__main__ import HELPABLE
        label = query.data.replace("cat_", "", 1)
        # Lookup category mapping built earlier
        mapping = getattr(app, "CATEGORY_MAP", {})
        modules = mapping.get(label, [])
        if not modules:
            # If something goes wrong, fall back to normal paginate
            keyboard = InlineKeyboardMarkup(paginate_modules_pyrogram(0, HELPABLE, "help"))
            text = "<b>Modules</b>"
        else:
            parts = [f"<b>{label} Commands</b>\n"]
            for key in modules:
                mod = HELPABLE.get(key)
                if not mod:
                    continue
                title = getattr(mod, "__mod_name__", key).strip()
                help_text = getattr(mod, "__help__", "No help available.")
                parts.append(f"<b>• {title}</b>\n{help_text}\n")
            text = "\n".join(parts)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="help_back")]])

        has_photo = query.message.photo or query.message.video or query.message.document
        if has_photo:
            try:
                await query.message.edit_caption(caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard)
            except Exception:
                await query.message.reply_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
        else:
            try:
                await query.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
            except Exception:
                pass
    except Exception:
        pass
    await query.answer()

@app.on_callback_query(filters.regex(r"^help_module\((.+?)\)$"))
async def cb_help_module(_, query: CallbackQuery):
    try:
        import re
        match = re.match(r"help_module\((.+?)\)", query.data)
        if match:
            module_name = match.group(1)
            from sitaBot.__main__ import HELPABLE
            if module_name in HELPABLE:
                mod_obj = HELPABLE[module_name]
                mod_display = mod_obj.__mod_name__ if hasattr(mod_obj, '__mod_name__') else module_name
                help_text = f"<b>📚 {mod_display}</b>\n\n"
                
                # Get help content
                help_content = mod_obj.__help__ if hasattr(mod_obj, '__help__') else "No help available."
                help_text += help_content
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Back", callback_data="help_back")]
                ])
                
                # Always try to edit the same message, don't send new one
                has_photo = query.message.photo or query.message.video or query.message.document
                if has_photo:
                    try:
                        await query.message.edit_caption(
                            caption=help_text,
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=keyboard,
                        )
                    except Exception:
                        # If edit fails, try to convert to text message by deleting and editing
                        try:
                            # Delete photo message and send text
                            chat_id = query.message.chat.id
                            await query.message.delete()
                            await _.send_message(
                                chat_id,
                                help_text,
                                parse_mode=enums.ParseMode.HTML,
                                reply_markup=keyboard,
                                disable_web_page_preview=True
                            )
                        except Exception:
                            pass
                else:
                    try:
                        await query.message.edit_text(
                            help_text,
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=keyboard,
                            disable_web_page_preview=True
                        )
                    except Exception:
                        pass
    except Exception:
        pass
    await query.answer()


@app.on_callback_query(filters.regex(r"^help_prev\((.+?)\)$"))
async def cb_help_prev(_, query: CallbackQuery):
    try:
        import re
        match = re.match(r"help_prev\((.+?)\)", query.data)
        if match:
            curr_page = int(match.group(1))
            from sitaBot.__main__ import HELPABLE, HELP_STRINGS
            help_text = HELP_STRINGS.replace("Markdown", "HTML").replace("*", "").replace("_", "")
            if not help_text.strip():
                help_text = (
                    "<b>⚙️ Help & Commands</b>\n\n"
                    "• Click a module below to see commands and usage\n"
                    "• All commands use the <code>/</code> prefix"
                )
            keyboard = InlineKeyboardMarkup(paginate_modules_pyrogram(curr_page - 1, HELPABLE, "help"))
            
            has_photo = query.message.photo or query.message.video or query.message.document
            if has_photo:
                try:
                    await query.message.edit_caption(
                        caption=help_text,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=keyboard,
                    )
                except Exception:
                    await query.message.reply_text(
                        help_text,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
            else:
                try:
                    await query.message.edit_text(
                        help_text,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
                except Exception:
                    pass
    except Exception:
        pass
    await query.answer()


@app.on_callback_query(filters.regex(r"^help_next\((.+?)\)$"))
async def cb_help_next(_, query: CallbackQuery):
    try:
        import re
        match = re.match(r"help_next\((.+?)\)", query.data)
        if match:
            next_page = int(match.group(1))
            from sitaBot.__main__ import HELPABLE, HELP_STRINGS
            help_text = HELP_STRINGS.replace("Markdown", "HTML").replace("*", "").replace("_", "")
            if not help_text.strip():
                help_text = (
                    "<b>⚙️ Help & Commands</b>\n\n"
                    "• Click a module below to see commands and usage\n"
                    "• All commands use the <code>/</code> prefix"
                )
            keyboard = InlineKeyboardMarkup(paginate_modules_pyrogram(next_page + 1, HELPABLE, "help"))
            
            has_photo = query.message.photo or query.message.video or query.message.document
            if has_photo:
                try:
                    await query.message.edit_caption(
                        caption=help_text,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=keyboard,
                    )
                except Exception:
                    await query.message.reply_text(
                        help_text,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
            else:
                try:
                    await query.message.edit_text(
                        help_text,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
                except Exception:
                    pass
    except Exception:
        pass
    await query.answer()


@app.on_callback_query(filters.regex(r"^sita_back$"))
async def cb_sita_back(_, query: CallbackQuery):
    try:
        caption = (
            "<b>✨ ɪɴɴᴇxɪᴀ ʙᴏᴛ</b> is online and ready to help!\n\n"
            "ʏᴏᴜʀ ᴀʟʟ‑ɪɴ‑ᴏɴᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ + ғᴜɴ ʙᴏᴛ:\n"
            "• ᴀᴅᴍɪɴ ᴛᴏᴏʟs (ʙᴀɴ/ᴍᴜᴛᴇ/ᴘɪɴ)\n"
            "• ᴡᴀʀɴs, ᴀɴᴛɪғʟᴏᴏᴅ, ғɪʟᴛᴇʀs, ɴᴏᴛᴇs\n"
            "• ꜱᴛɪᴄᴋᴇʀ/ᴍᴇᴅɪᴀ ᴛᴏᴏʟs, ᴛʀᴀɴꜱʟᴀᴛᴏʀ, ᴡɪᴋɪ, ᴀɪ ᴄʜᴀᴛ\n\n"
            "<i>© 2025‑26 <a href=\"https://t.me/about_brahix\">brahix Bots</a> ("
            "<a href=\"https://t.me/brahix\">brahix</a>) · Powered by "
            "<a href=\"https://t.me/brahix\">BRAHIX</a></i>\n\n"
            f"<b>ʜᴇʟʟᴏ</b> {query.from_user.mention if query.from_user else ''}\n"
            "ɪ'ᴍ ʏᴏᴜʀ ɢʀᴏᴜᴘ ʜᴇʟᴘᴇʀ + ғᴜɴ ʙᴏᴛ. ʟᴇᴛ'ꜱ ɢᴇᴛ ꜱᴛᴀʀᴛᴇᴅ!"
        )
        try:
            await query.message.edit_caption(
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=private_keyboard(),
            )
        except Exception:
            await query.message.edit_text(
                caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=private_keyboard(),
                disable_web_page_preview=True
            )
    except Exception:
        pass
    await query.answer()

