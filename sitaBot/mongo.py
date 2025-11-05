import asyncio
import sys

from motor import motor_asyncio
from sitaBot import MONGO_DB_URI, LOGGER
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Extract database name from URI or default to destinymusic
MONGO_DB = "destinymusic"
if MONGO_DB_URI and "/" in MONGO_DB_URI.split("?")[0]:
    try:
        db_part = MONGO_DB_URI.split("/")[-1].split("?")[0]
        if db_part:
            MONGO_DB = db_part
    except Exception:
        pass

# Only initialize if MONGO_DB_URI is provided
if MONGO_DB_URI:
    client = MongoClient(MONGO_DB_URI)[MONGO_DB]
    motor = motor_asyncio.AsyncIOMotorClient(MONGO_DB_URI)
    db = motor[MONGO_DB]
    try:
        asyncio.get_event_loop().run_until_complete(motor.server_info())
    except ServerSelectionTimeoutError:
        LOGGER.critical("Can't connect to mongodb! Exiting...")
        sys.exit(1)
else:
    # Fallback if MongoDB is not configured
    client = None
    motor = None
    db = None