"""
NSFW Detection Module for Sita Chatbot
Integrates NSFW detection from nsfw_bot into sita-chatbot architecture
"""
import os
import sys
import logging
import tempfile
import asyncio
from typing import Optional, Dict
from pathlib import Path

# Import NSFW detection modules from integrated locations
try:
    from sitaBot.modules.helper_funcs.nsfw_predict import detect_nsfw
    from sitaBot.modules.sql.nsfw_detection_sql import Database
    import sitaBot.modules.sql_extended.nsfw_watch_sql as nsfw_watch_sql
except ImportError as e:
    logging.error(f"Failed to import NSFW detection modules: {e}")
    detect_nsfw = None
    Database = None

from sitaBot import dispatcher, OWNER_ID, EVENT_LOGS
from sitaBot.modules.helper_funcs.chat_status import user_admin
from sitaBot.modules.helper_funcs.filters import CustomFilters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, run_async
from telegram.error import BadRequest
from PIL import Image
import imageio
import numpy as np
import zipfile
import json
import base64

logger = logging.getLogger(__name__)

# Initialize database
if Database:
    try:
        # Use database in root directory
        root_path = Path(__file__).parent.parent.parent.parent
        db_path = root_path / "nsfw_bot.db"
        nsfw_db = Database(str(db_path))
        # Database is initialized synchronously in __init__, so no need for async init
    except Exception as e:
        logger.error(f"Failed to initialize NSFW database: {e}")
        nsfw_db = None
else:
    nsfw_db = None

# Media directory - use temp directory or create in root
root_path = Path(__file__).parent.parent.parent.parent
MEDIA_DIR = root_path / "nsfw_media"
MEDIA_DIR.mkdir(exist_ok=True)


class MediaConverter:
    """Convert various media formats for NSFW detection"""
    
    @staticmethod
    def convert_webp_to_png(file_path: str) -> Optional[str]:
        """Convert WebP to PNG"""
        try:
            png_path = f"{tempfile.mktemp()}.png"
            with Image.open(file_path) as img:
                img.convert("RGB").save(png_path, "PNG")
            return png_path
        except Exception as e:
            logger.error(f"WebP conversion failed: {e}")
            return None

    @staticmethod
    def extract_frame_from_webm(input_path: str) -> Optional[str]:
        """Extract frame from WebM"""
        try:
            output_path = f"{tempfile.mktemp()}.jpg"
            with imageio.get_reader(input_path, format="webm") as reader:
                frame = reader.get_next_data()
                imageio.imwrite(output_path, np.array(frame, dtype=np.uint8), format="JPEG")
            return output_path
        except Exception as e:
            logger.error(f"WEBM frame extraction failed: {e}")
            return None

    @staticmethod
    def convert_tgs_to_png(file_path: str) -> Optional[str]:
        """Convert TGS to PNG"""
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                with z.open('animation.json') as f:
                    animation_data = json.load(f)
            
            output_path = f"{tempfile.mktemp()}.png"
            
            for asset in animation_data.get('assets', []):
                if 'p' in asset:
                    img_data = base64.b64decode(asset['p'].split(',')[1])
                    with open(output_path, 'wb') as f:
                        f.write(img_data)
                    return output_path
            
            Image.new('RGB', (512, 512), (255, 255, 255)).save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"TGS conversion failed: {e}")
            return None


def extract_video_frame(video_path: str) -> Optional[str]:
    """Extract frame from video using OpenCV"""
    try:
        import cv2
        output_path = f"{tempfile.mktemp()}.jpg"
        vidcap = cv2.VideoCapture(video_path)
        success, image = vidcap.read()
        if success:
            cv2.imwrite(output_path, image)
            return output_path
        return None
    except Exception as e:
        logger.error(f"OpenCV frame extraction failed: {e}")
        return None


@run_async
async def handle_media_nsfw(update: Update, context: CallbackContext):
    """Handle media messages for NSFW detection"""
    if not detect_nsfw or not nsfw_db:
        return  # NSFW detection not available
    
    # Check if detect_nsfw function is callable (model loaded)
    if not callable(detect_nsfw):
        return
    
    if not update.message or not update.message.from_user:
        return
    
    user = update.message.from_user
    chat = update.effective_chat
    
    # Skip if owner
    if user.id == OWNER_ID:
        return
    
    # Check if NSFW watch is enabled for this chat
    if not nsfw_watch_sql.is_nsfw_watch_enabled(chat.id):
        return
    
    # Check if user is approved (skip detection)
    try:
        if await nsfw_db.is_approved(user.id):
            return
    except:
        pass
    
    original_path = None
    processed_path = None
    
    try:
        # Handle different media types
        file = None
        file_extension = None
        
        if update.message.photo:
            file = update.message.photo[-1]  # Get highest resolution
            file_extension = ".jpg"
        elif update.message.video:
            file = update.message.video
            file_extension = ".mp4"
        elif update.message.sticker:
            file = update.message.sticker
            if file.is_animated:
                file_extension = ".tgs"
            elif file.is_video:
                file_extension = ".webm"
            else:
                file_extension = ".webp"
        elif update.message.document:
            file = update.message.document
            if file.file_name:
                file_extension = os.path.splitext(file.file_name)[1]
            else:
                return
        else:
            return  # Unsupported media type
        
        if not hasattr(file, "file_id"):
            return
        
        # Download file
        file_obj = await context.bot.get_file(file.file_id)
        original_path = str(MEDIA_DIR / f"{user.id}_{file.file_id}{file_extension}")
        await file_obj.download_to_drive(original_path)
        
        if not os.path.exists(original_path):
            logger.error(f"Download failed: {original_path}")
            return
        
        # Process based on media type
        if update.message.video:
            processed_path = extract_video_frame(original_path)
        elif update.message.sticker:
            if file.is_animated:
                processed_path = MediaConverter.convert_tgs_to_png(original_path)
            elif file.is_video:
                processed_path = MediaConverter.extract_frame_from_webm(original_path)
            else:
                processed_path = MediaConverter.convert_webp_to_png(original_path)
        else:
            processed_path = original_path
        
        if not processed_path or not os.path.exists(processed_path):
            logger.error(f"Processing failed for {original_path}")
            return
        
        # NSFW Detection
        result = detect_nsfw(processed_path)
        if not result:
            return
        
        max_category = max(result, key=result.get)
        if max_category in ["porn", "sexy", "hentai"]:
            await handle_nsfw_violation(update, context, user, chat.id, result, max_category)
    
    except Exception as e:
        logger.error(f"Media handling error: {e}", exc_info=True)
    finally:
        # Cleanup files
        for path in [original_path, processed_path]:
            try:
                if path and os.path.exists(path) and path != original_path:
                    os.remove(path)
            except Exception as e:
                logger.warning(f"Cleanup failed for {path}: {e}")


async def handle_nsfw_violation(
    update: Update,
    context: CallbackContext,
    user,
    chat_id: int,
    result: Dict[str, float],
    max_category: str,
):
    """Handle NSFW violation"""
    try:
        # Delete the message
        try:
            await update.message.delete()
        except BadRequest as e:
            logger.warning(f"Couldn't delete message: {e}")
        
        # Update violations in database
        try:
            await nsfw_db.update_violations(user.id, max_category)
        except:
            pass
        
        # Send user alert
        user_alert = format_user_alert(user, result)
        try:
            await context.bot.send_message(
                chat_id,
                user_alert,
                parse_mode="Markdown"
            )
        except BadRequest as e:
            logger.warning(f"Couldn't send user alert: {e}")
        
        # Send admin alert to log channel
        if EVENT_LOGS:
            admin_alert = format_admin_alert(user, result, chat_id, update)
            try:
                await context.bot.send_message(
                    EVENT_LOGS,
                    admin_alert,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("👤 View Profile", url=f"tg://user?id={user.id}")]
                    ]),
                    parse_mode="Markdown"
                )
            except BadRequest as e:
                if "Button_user_privacy_restricted" not in str(e):
                    logger.warning(f"Couldn't send admin alert: {e}")
    
    except Exception as e:
        logger.error(f"Violation handling failed: {e}", exc_info=True)


def format_user_alert(user, result: Dict[str, float]) -> str:
    """Format the user alert message"""
    return f"""
╭─────────────────
╰──📎 ɴsғᴡ ᴅᴇᴛᴇᴄᴛᴇᴅ 🔞
╭❁╼━━━━━━❖━━━━━━━❁╮ 
│❏ ᴜsᴇʀ: {user.id}
│❏ ᴜsᴇʀɴᴀᴍᴇ: @{user.username or 'None'}
│❏ ᴅᴇᴛᴀɪʟs:
│❏ ᴅʀᴀᴡɪɴɢs: {result.get('drawings', 0):.2f}
│❏ ɴᴇᴜᴛʀᴀʟ: {result.get('neutral', 0):.2f}
│❏ ᴘᴏʀɴ: {result.get('porn', 0):.2f}
│❏ ʜᴇɴᴛᴀɪ: {result.get('hentai', 0):.2f}
│❏ sᴇxʏ: {result.get('sexy', 0):.2f}
╰❁╼━━━━━━❖━━━━━━━❁╯"""


def format_admin_alert(user, result: Dict[str, float], chat_id: int, update: Update) -> str:
    """Format the admin alert message"""
    return f"""
🚨 NSFW DETECTED 🔞

User: {user.id}
Username: @{user.username or 'None'}
First Name: {user.first_name or 'None'}
Last Name: {user.last_name or 'None'}

Detection Scores:
Drawings: {result.get('drawings', 0):.2f}
Neutral: {result.get('neutral', 0):.2f}
Porn: {result.get('porn', 0):.2f}
Hentai: {result.get('hentai', 0):.2f}
Sexy: {result.get('sexy', 0):.2f}

Chat ID: {chat_id}
Message ID: {update.message.message_id if update.message else 'N/A'}"""


@run_async
@user_admin
def enable_nsfw_watch(update: Update, context: CallbackContext):
    """Enable NSFW watch for the chat"""
    chat = update.effective_chat
    if nsfw_watch_sql.is_nsfw_watch_enabled(chat.id):
        update.effective_message.reply_text("NSFW watch is already enabled for this chat!")
        return
    
    nsfw_watch_sql.enable_nsfw_watch(chat.id)
    update.effective_message.reply_text("✅ NSFW watch enabled! The bot will now detect and delete NSFW content.")


@run_async
@user_admin
def disable_nsfw_watch(update: Update, context: CallbackContext):
    """Disable NSFW watch for the chat"""
    chat = update.effective_chat
    if not nsfw_watch_sql.is_nsfw_watch_enabled(chat.id):
        update.effective_message.reply_text("NSFW watch is already disabled for this chat!")
        return
    
    nsfw_watch_sql.disable_nsfw_watch(chat.id)
    update.effective_message.reply_text("❌ NSFW watch disabled.")


# Register handlers
if detect_nsfw and nsfw_db:
    try:
        NSFW_WATCH_ENABLE_HANDLER = CommandHandler("nsfwwatch", enable_nsfw_watch, filters=Filters.chat_type.groups)
        NSFW_WATCH_DISABLE_HANDLER = CommandHandler("nsfwunwatch", disable_nsfw_watch, filters=Filters.chat_type.groups)
        NSFW_MEDIA_HANDLER = MessageHandler(
            Filters.photo | Filters.video | Filters.sticker | Filters.document,
            handle_media_nsfw
        )
        
        dispatcher.add_handler(NSFW_WATCH_ENABLE_HANDLER)
        dispatcher.add_handler(NSFW_WATCH_DISABLE_HANDLER)
        dispatcher.add_handler(NSFW_MEDIA_HANDLER)
        logger.info("NSFW detection module loaded successfully")
    except Exception as e:
        logger.error(f"Failed to register NSFW detection handlers: {e}")
else:
    logger.warning("NSFW detection not available - missing dependencies or model")

__mod_name__ = "NSFW Detection"
__help__ = """
*NSFW Detection:*
• `/nsfwwatch` - Enable NSFW detection for this chat
• `/nsfwunwatch` - Disable NSFW detection for this chat

The bot will automatically detect and delete NSFW content when enabled.
"""

