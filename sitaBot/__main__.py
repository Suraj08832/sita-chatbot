import importlib
import time
import re
from sys import argv
from typing import Optional

from sitaBot import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,
    dispatcher,
    StartTime,
    telethn,
    pbot,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from sitaBot.modules import ALL_MODULES
from sitaBot.modules.helper_funcs.chat_status import is_user_admin
from sitaBot.modules.helper_funcs.misc import paginate_modules
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """```
❖ sɪᴛᴧ ʙσᴛ ❖```
**✨ ʜєʟʟσ, ɪ'ᴍ sɪᴛᴧ ʙσᴛ!**

**ʏσυʀ ᴧʟʟ-ɪη-σηє ɢʀσυᴩ ϻᴧηᴧɢєϻєηᴛ + ғυη ʙσᴛ:**

❍ ᴧᴅϻɪη ᴛσσʟs (ʙᴧη/ϻυᴛє/ᴩɪη) ⚡
❍ ᴡᴧʀηs, ᴧηᴛɪғʟσσᴅ, ғɪʟᴛєʀs, ησᴛєs 📝
❍ sᴛɪᴄᴋєʀ/ϻєᴅɪᴧ ᴛσσʟs, ᴛʀᴧηsʟᴧᴛσʀ, ᴡɪᴋɪ, ᴧɪ ᴄʜᴧᴛ 🎨
❍ єᴄσησϻʏ sʏsᴛєϻ: ʀσʙ, ᴋɪʟʟ, ʟσᴛᴛєʀʏ 💰

**❖ 𝐏ᴏᴡᴇʀᴇᴅ 𝖡ʏ » [𝆺𝅥⃝🎧×⃪͜‌ 𝐁 𝐑 𝐀 𝐇 𝐈 𝐗 ◡̈⃝⟶📻](https://t.me/brahix)**
"""

buttons = [
    [
        InlineKeyboardButton(
            text="• ʜєʟᴩ & ᴄσϻϻᴧηᴅs •", callback_data="help_back"),
    ],
    [
        InlineKeyboardButton(text="˹ sυᴩᴩσʀᴛ ˼", url=f"https://t.me/brahix_support"),
        InlineKeyboardButton(
            text="˹ υᴩᴅᴧᴛєs ˼", url=f"https://t.me/about_brahix"
        ),
    ],
    [
        InlineKeyboardButton(text="˹ ᴧʙσυᴛ ˼", callback_data="sita_"),
        InlineKeyboardButton(
            text="˹ єᴄσησϻʏ ˼", callback_data="economy_help"
        ),
    ],
    [
        InlineKeyboardButton(text="➕ ᴧᴅᴅ ᴛσ ɢʀσυᴩ ➕", url="http://t.me/Sitabot?startgroup=true"),
    ],
]


HELP_STRINGS = """```
❖ ʜєʟᴩ & ᴄσϻϻᴧηᴅs ❖```
**ᴄʜσσsє ᴛʜє ᴄᴧᴛєɢσʀʏ ғσʀ ᴡʜɪᴄʜ ʏσυ ᴡᴧηηᴧ ɢєᴛ ʜєʟᴩ**

**❍ ᴄʟɪᴄᴋ ᴧ ᴄᴧᴛєɢσʀʏ ʙєʟσᴡ ᴛσ ʙʀσᴡsє ᴄσϻϻᴧηᴅs 📚
❍ ᴧʟʟ ᴄσϻϻᴧηᴅs υsє ᴛʜє / ᴩʀєғɪx 💬
❍ ηєєᴅ ʜєʟᴩ? ᴊσɪη <a href="https://t.me/brahix_support">sυᴩᴩσʀᴛ</a> 🆘

❖ 𝐏ᴏᴡᴇʀᴇᴅ 𝖡ʏ » [𝆺𝅥⃝🎧×⃪͜‌ 𝐁 𝐑 𝐀 𝐇 𝐈 𝐗 ◡̈⃝⟶📻](https://t.me/brahix)**
"""

# Module categorization
MANAGEMENT_MODULES = [
    "approvals", "ban/mute", "warn", "locks", "bluetext cleaning", 
    "backup", "blacklist", "stickers b list", "blacklisting users",
    "control", "purge", "detele", "greetings", "rules", "reports",
    "notes", "filters", "admin", "connections", "pin", "disabled", 
    "channel", "federations"
]

GAMES_FUN_MODULES = [
    "economy", "couples", "anime", "extras", "quotly", "logo", 
    "infos", "users", "sed/regex", "math"
]

ADVANCED_MODULES = [
    "nsfw", "forcesubs", "shield", "nightmode", "antiflood",
    "dbcleanup", "modules", "shell"
]



DONATE_STRING = """Heya, glad to hear you want to donate!
 @brahix 💕"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("sitaBot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# Helper function to create category buttons with stylish fonts
def get_category_buttons():
    return [
        [
            InlineKeyboardButton("⚙️ ᴍᴧηᴧɢєϻєηᴛ ⚙️", callback_data="help_category_management")
        ],
        [
            InlineKeyboardButton("🎮 ɢᴧϻєs & ғυη 🎮", callback_data="help_category_games")
        ],
        [
            InlineKeyboardButton("🔥 ᴧᴅᴠᴧηᴄєᴅ ϻσᴅυʟєs 🔥", callback_data="help_category_advanced")
        ],
        [
            InlineKeyboardButton("🏠 ʜσϻє 🏠", callback_data="sita_back")
        ]
    ]

# Helper function to get modules by category
def get_modules_for_category(category):
    category_map = {
        "management": MANAGEMENT_MODULES,
        "games": GAMES_FUN_MODULES,
        "advanced": ADVANCED_MODULES
    }
    
    category_modules = category_map.get(category, [])
    available_modules = {}
    
    for mod_name in category_modules:
        if mod_name.lower() in HELPABLE:
            available_modules[mod_name.lower()] = HELPABLE[mod_name.lower()]
    
    return available_modules

# Helper function to create module buttons for a category
def create_module_buttons(category):
    modules = get_modules_for_category(category)
    buttons = []
    
    module_list = list(modules.items())
    
    # Create buttons in rows of 2
    for i in range(0, len(module_list), 2):
        row = []
        for j in range(i, min(i + 2, len(module_list))):
            mod_name, mod = module_list[j]
            display_name = mod.__mod_name__
            # Use stylish font for button text
            row.append(InlineKeyboardButton(
                f"• {display_name} •",
                callback_data=f"help_module({mod_name})"
            ))
        buttons.append(row)
    
    # Add back button
    buttons.append([InlineKeyboardButton("⬅️ ʙᴧᴄᴋ ⬅️", callback_data="help_back")])
    
    return buttons

# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(get_category_buttons())
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


@run_async
def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@run_async
def start(update: Update, context: CallbackContext):
    # This handler is for telegram bot (python-telegram-bot) as fallback
    # Pyrogram bot (pbot) handles start via start_stylish.py - so skip simple /start
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="⬅️ BACK", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)
            else:
                # For other args, let pyrogram handle it or just return
                return
        else:
            # Simple /start without args - let Pyrogram handle it, don't send duplicate
            return
    else:
        update.effective_message.reply_text(
            "<b>👋 ɪ'ᴍ ᴀᴡᴀᴋᴇ ᴀʟʀᴇᴀᴅʏ!</b>\n<small>ʜᴀᴠᴇɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ:</small> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    category_match = re.match(r"help_category_(.+)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            # Show specific module help
            module = mod_match.group(1)
            if module.lower() in HELPABLE:
                mod_obj = HELPABLE[module.lower()]
                text = f"```\n❖ {mod_obj.__mod_name__.upper()} ❖```\n\n{mod_obj.__help__}\n\n**❖ 𝐏ᴏᴡᴇʀᴇᴅ 𝖡ʏ » [𝆺𝅥⃝🎧×⃪͜‌ 𝐁 𝐑 𝐀 𝐇 𝐈 𝐗 ◡̈⃝⟶📻](https://t.me/brahix)**"
                
                query.message.edit_text(
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="⬅️ ʙᴧᴄᴋ ⬅️", callback_data="help_back")]]
                    ),
                )

        elif category_match:
            # Show modules for the selected category
            category = category_match.group(1)
            
            category_titles = {
                "management": "```\n❖ ᴍᴧηᴧɢєϻєηᴛ ϻσᴅυʟєs ❖```\n\n**ᴄʟɪᴄᴋ ση ᴧ ϻσᴅυʟє ᴛσ sєє ɪᴛs ᴄσϻϻᴧηᴅs ⚙️**\n\n**❖ 𝐏ᴏᴡᴇʀᴇᴅ 𝖡ʏ » [𝆺𝅥⃝🎧×⃪͜‌ 𝐁 𝐑 𝐀 𝐇 𝐈 𝐗 ◡̈⃝⟶📻](https://t.me/brahix)**",
                "games": "```\n❖ ɢᴧϻєs & ғυη ϻσᴅυʟєs ❖```\n\n**ᴄʟɪᴄᴋ ση ᴧ ϻσᴅυʟє ᴛσ sєє ɪᴛs ᴄσϻϻᴧηᴅs 🎮**\n\n**❖ 𝐏ᴏᴡᴇʀᴇᴅ 𝖡ʏ » [𝆺𝅥⃝🎧×⃪͜‌ 𝐁 𝐑 𝐀 𝐇 𝐈 𝐗 ◡̈⃝⟶📻](https://t.me/brahix)**",
                "advanced": "```\n❖ ᴧᴅᴠᴧηᴄєᴅ ϻσᴅυʟєs ❖```\n\n**ᴄʟɪᴄᴋ ση ᴧ ϻσᴅυʟє ᴛσ sєє ɪᴛs ᴄσϻϻᴧηᴅs 🔥**\n\n**❖ 𝐏ᴏᴡᴇʀᴇᴅ 𝖡ʏ » [𝆺𝅥⃝🎧×⃪͜‌ 𝐁 𝐑 𝐀 𝐇 𝐈 𝐗 ◡̈⃝⟶📻](https://t.me/brahix)**"
            }
            
            text = category_titles.get(category, HELP_STRINGS)
            buttons = create_module_buttons(category)
            
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(buttons),
            )

        elif back_match:
            # Go back to category selection
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(get_category_buttons()),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)

    except BadRequest as e:
        print(f"BadRequest in help_button: {e}")
        pass


@run_async
def sita_about_callback(update, context):
    query = update.callback_query
    if query.data == "sita_":
        query.message.edit_text(
            text=""" **INNEXIA** it's online since 29 March 2021 and it's constantly updated!
            \n**Bot Admins**
            
            \n• @brahix, bot creator and main developer.
            \n• The Doctor, server manager and developer.
            \n• Manuel 5, developer.
            \n**Support**
            \n• [Click here](t.me/BotDevlopers) to consult the updated list of Official Supporters of the bot.
            \n• Thanks to all our **donors** for supporting server and development expenses and all those who have reported bugs or suggested new features.
            \n• We also thank **all the groups** who rely on our Bot for this service, we hope you will always like it: we are constantly working to improve it!""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Back", callback_data="sita_back")
                 ]
                ]
            ),
        )
    elif query.data == "sita_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )


@run_async
def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text=""" Hi..😻 I'm *Sita*
                 \nHere is the [🔥Source Code🔥](https://brahix) .""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Go Back", callback_data="source_back")
                 ]
                ]
            ),
        )
    elif query.data == "source_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )

@run_async
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Help",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


@run_async
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


@run_async
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 1947924017 and DONATION_LINK:
            update.effective_message.reply_text(
                "You can also donate to the person currently running me "
                "[here]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@{SUPPORT_CHAT}", "`Yes I'm Fine` 😹")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start)  # Fallback handler for telegram bot

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(sita_about_callback, pattern=r"sita_")
    source_callback_handler = CallbackQueryHandler(Source_about_callback, pattern=r"source_")

    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)  # Fallback for telegram bot, pyrogram uses start_stylish.py
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
