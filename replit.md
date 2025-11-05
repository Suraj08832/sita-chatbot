# sitaBot - Telegram Group Management Bot

## Overview
sitaBot is a feature-rich Telegram group management bot with comprehensive admin tools, entertainment features, and an advanced economy system. Originally forked from innexiaBot, it has been enhanced with stylish Unicode fonts and a complete economy module.

**Current Status**: ✅ Running successfully
**Last Updated**: November 5, 2025

## Key Features

### Admin & Moderation
- User bans, kicks, mutes, and warnings
- Anti-flood protection
- Blacklist words and stickers
- Approval system for users
- Fed (Federation) system for cross-group management
- Night mode (scheduled group locking)
- Zombie (deleted accounts) cleanup

### Entertainment & Fun
- Games (truth or dare, dice, etc.)
- AI chatbot integration
- Anime info lookup
- Music downloads
- Fun text generators (mock, zalgo, etc.)
- Shipping game
- Quotly (quote maker)
- Sticker tools
- Wikipedia search
- Weather info

### Economy System 💰
Complete economy module with:
- **Balance Management**: Check and manage user balances
- **Rob Command**: 50% success rate to steal from others
- **Kill/Revive**: 60% kill success, death penalties, revival system
- **Protection**: Shield yourself from robberies
- **Lottery**: Gambling system with random rewards
- **Items**: Gift items between users with inventory tracking
- **Daily Bonuses**: Reward active users
- **Global Leaderboards**: Track richest users and top killers

### Utilities
- Currency converter
- Google Translator
- Time zone lookup
- Speed test
- Text-to-speech & Speech-to-text
- Telegraph uploader
- Lyrics finder
- Logo maker
- QR code generator

## Project Architecture

### Technology Stack
- **Python**: 3.9
- **Bot Framework**: python-telegram-bot 12.8
- **Additional Libraries**: Telethon 1.16.4, Pyrogram
- **Databases**: 
  - PostgreSQL (via SQLAlchemy) - for user data, settings, economy
  - MongoDB - for some modular features
- **Background Jobs**: APScheduler for scheduled tasks

### Directory Structure
```
sitaBot/
├── __init__.py           # Bot initialization, database connections
├── __main__.py          # Main entry point, module loader
├── config.py            # Configuration (uses environment variables)
├── modules/             # Feature modules
│   ├── economy.py       # Economy system commands
│   ├── start_stylish.py # Stylish start/help with Unicode fonts
│   ├── admin.py         # Admin commands
│   ├── bans.py          # Ban management
│   ├── fun.py           # Fun commands
│   └── sql/             # Database schemas
│       └── economy_sql.py
├── sample_config.py     # Sample configuration template
└── requirements.txt     # Python dependencies
```

### Recent Changes

#### November 5, 2025 - Complete Transformation
1. **Security Enhancement**
   - Removed all hardcoded API keys from config.py
   - Migrated to Replit Secrets for all sensitive data
   - Added comprehensive .gitignore

2. **Rebranding**
   - Renamed entire codebase from "innexiaBot" to "sitaBot"
   - Updated all references across 50+ files
   - Changed bot mention from @InnexiaBot to @sitaBot

3. **Economy System Implementation**
   - Added complete economy module (`economy.py`)
   - Created economy database schema (`economy_sql.py`)
   - Features: rob, kill, revive, protect, lottery, items/gifting
   - Global tracking with leaderboards

4. **UI Enhancement**
   - Updated start/help buttons with fancy Unicode fonts
   - Improved visual appeal: ʙᴏᴛ, ᴀʙᴏᴜᴛ, sᴜᴘᴘᴏʀᴛ, ᴜᴘᴅᴀᴛᴇs, ʜᴇʟᴘ

5. **Environment Setup**
   - Installed Python 3.9
   - Configured all 60+ dependencies
   - Set up Replit workflow for auto-restart

## Configuration

### Required Environment Variables (Replit Secrets)
All sensitive configuration is stored in Replit Secrets:

#### Core Bot Settings
- `TOKEN` - Telegram Bot Token from @BotFather
- `API_ID` - Telegram API ID from my.telegram.org
- `API_HASH` - Telegram API Hash from my.telegram.org
- `OWNER_ID` - Telegram user ID of bot owner

#### Database Settings
- `SQLALCHEMY_DATABASE_URI` - PostgreSQL connection string
- `MONGO_DB_URI` - MongoDB connection string

#### Optional Settings
- `BOT_ID` - Bot's Telegram ID
- `ENV` - Environment (set to "PRODUCTION")
- `EVENT_LOGS` - Channel ID for event logging
- `JOIN_LOGGER` - Channel ID for join/leave logs
- `SPAMWATCH_API` - SpamWatch API key (optional)
- `GENIUS_API_TOKEN` - Genius lyrics API (optional)

### Module Loading
The bot automatically loads all modules from `sitaBot/modules/` except those in the blacklist. Currently not loading:
- `translation` (disabled)

All other 100+ modules are active including the new economy module.

## Database Schema

### Economy Tables
- **user_economy**: Stores user balances, kills, deaths
- **user_protection**: Tracks protection status and expiry
- **user_items**: User inventory system
- **lottery_history**: Lottery participation records

## Development Notes

### Code Conventions
- Uses snake_case for functions and variables
- Handlers follow pattern: `@run_async` decorator for non-blocking
- SQL operations use SQLAlchemy ORM
- Error handling with try-except blocks
- Logging via Python logging module

### Adding New Modules
1. Create file in `sitaBot/modules/`
2. Import necessary handlers from `telegram.ext`
3. Define command handlers with `@run_async`
4. Add to `__HANDLERS__` list at bottom
5. Optionally add to `__mod_name__` and `__help__`

### Database Migrations
- Currently using direct SQLAlchemy Base.metadata.create_all()
- For production, consider using Alembic for migrations

## User Preferences
- **Security First**: Always use environment variables, never hardcode secrets
- **Clean Code**: Remove unused code, maintain organized file structure
- **Documentation**: Keep this file updated with major changes

## Workflow

### Running the Bot
The bot runs automatically via the Replit workflow:
```bash
python3 -m sitaBot
```

### Stopping/Restarting
- Use the Replit UI to stop/restart the workflow
- Bot will auto-restart on code changes (via workflow)

## Known Issues & Warnings
- `SpamWatch API key missing` - Optional feature, not critical
- `No str key: GENIUS_API_TOKEN` - Optional for lyrics, not critical
- LSP diagnostics in economy files - minor type warnings, not affecting functionality

## Future Enhancements (Potential)
- Add more economy features (shops, auctions, trading)
- Implement web dashboard for bot management
- Add more games and entertainment modules
- Enhance anti-spam with machine learning
- Add support for more languages

## Support & Resources
- **Bot Username**: @sitaBot (configure in Telegram)
- **Original Source**: innexiaBot (heavily modified)
- **Python Telegram Bot Docs**: https://python-telegram-bot.readthedocs.io/

## Dependencies Summary
Over 60 packages installed including:
- python-telegram-bot, Telethon, Pyrogram (bot frameworks)
- SQLAlchemy, pymongo (databases)
- APScheduler (task scheduling)
- lxml, BeautifulSoup4 (parsing)
- And many specialized libraries for features

## License
Inherited from innexiaBot - Check original repository for license terms.

---

**Note**: This bot is fully functional and running. All core features including the new economy system are operational. Make sure all required environment variables are set in Replit Secrets before starting.
