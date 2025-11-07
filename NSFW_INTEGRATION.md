# NSFW Bot Integration

This document describes the integration of the NSFW Bot into Sita Chatbot.

## Overview

The NSFW Bot has been successfully integrated directly into the sita-chatbot project structure. All important files have been moved from the separate `nsfw_bot` folder into the main sita-chatbot structure:

1. **NSFW Detection Module** (`sitaBot/modules/nsfw_detection.py`)
   - Automatically detects NSFW content in images, videos, and stickers
   - Deletes detected NSFW content
   - Logs violations to the event log channel
   - Supports per-chat enable/disable functionality

2. **Database Integration** (`sitaBot/modules/sql/nsfw_detection_sql.py`)
   - Uses SQLite database for storing user violations and approved users
   - Database file: `nsfw_bot.db` (in root directory)

3. **Model Files** (`sitaBot/resources/nsfw_model/`)
   - NSFW detection model: `sitaBot/resources/nsfw_model/nsfw_mobilenet2.224x224.h5`
   - Uses TensorFlow/Keras for detection

4. **Prediction Module** (`sitaBot/modules/helper_funcs/nsfw_predict.py`)
   - Contains the NSFW detection logic
   - Handles model loading and image classification

## Commands

- `/nsfwwatch` - Enable NSFW detection for the current chat (admin only)
- `/nsfwunwatch` - Disable NSFW detection for the current chat (admin only)

## Configuration

The module automatically:
- Checks if NSFW watch is enabled for each chat
- Skips detection for approved users
- Skips detection for the bot owner
- Processes photos, videos, stickers, and documents

## Dependencies

All required dependencies have been added to `requirements.txt`:
- tensorflow
- tensorflow-hub
- opencv-python-headless
- imageio
- aiosqlite
- And other required packages

## File Structure

```
sita-chatbot/
├── nsfw_bot.db                 # NSFW detection database (root)
├── nsfw_media/                 # Temporary media storage
└── sitaBot/
    ├── modules/
    │   ├── nsfw_detection.py           # Main NSFW detection module
    │   ├── helper_funcs/
    │   │   └── nsfw_predict.py          # NSFW detection logic
    │   └── sql/
    │       └── nsfw_detection_sql.py    # Database handler
    └── resources/
        └── nsfw_model/                   # Model files
            ├── nsfw_mobilenet2.224x224.h5
            └── nsfw.txt
```

## Notes

- The module gracefully handles missing dependencies
- If TensorFlow is not available, the module will log a warning but won't crash
- The module is automatically loaded by sita-chatbot's module system
- Media files are temporarily stored in `nsfw_media/` during processing
- All NSFW bot files are now integrated directly into sita-chatbot structure
- No separate `nsfw_bot` folder exists - everything is part of the main project

## Troubleshooting

If NSFW detection is not working:
1. Check if TensorFlow is installed: `pip install tensorflow tensorflow-hub`
2. Verify the model file exists: `nsfw_bot/handlers/nsfw_model/nsfw_mobilenet2.224x224.h5`
3. Check logs for any import errors
4. Ensure the module is enabled in the chat using `/nsfwwatch`

