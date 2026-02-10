# utils/bot_utils.py
import os
import logging
from typing import List
from .json_utils import load_json, save_json
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger("ChurchBot.bot_utils")

DATA_DIR = os.getenv("DATA_DIR", "data")
ADMINS_FILE = os.path.join(DATA_DIR, "admins.json")
GROUPS_FILE = os.path.join(DATA_DIR, "groups.json")
PRAYERS_FILE = os.path.join(DATA_DIR, "prayers.json")
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")

def get_admins() -> List[str]:
    return load_json(ADMINS_FILE, [])

def add_admin(user_id: str) -> bool:
    admins = get_admins()
    if str(user_id) not in admins:
        admins.append(str(user_id))
        save_json(ADMINS_FILE, admins)
        return True
    return False

def remove_admin(user_id: str) -> bool:
    admins = get_admins()
    if str(user_id) in admins:
        admins.remove(str(user_id))
        save_json(ADMINS_FILE, admins)
        return True
    return False

def is_admin(user_id: str) -> bool:
    return str(user_id) in get_admins()

def get_groups():
    return load_json(GROUPS_FILE, [])

def add_group(group_id: str) -> bool:
    groups = get_groups()
    if str(group_id) not in groups:
        groups.append(str(group_id))
        save_json(GROUPS_FILE, groups)
        return True
    return False

def remove_group(group_id: str) -> bool:
    groups = get_groups()
    if str(group_id) in groups:
        groups.remove(str(group_id))
        save_json(GROUPS_FILE, groups)
        return True
    return False

def get_prayers():
    return load_json(PRAYERS_FILE, [])

def add_prayer(user_id: str, text: str) -> None:
    prayers = get_prayers()
    prayers.append({"user": str(user_id), "text": text})
    save_json(PRAYERS_FILE, prayers)

def get_events():
    return load_json(EVENTS_FILE, [])

def add_event(event: str) -> None:
    events = get_events()
    events.append(event)
    save_json(EVENTS_FILE, events)

def clear_events() -> None:
    save_json(EVENTS_FILE, [])

# Async error handler for Application
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled exception in update: %s", context.error)
    try:
        if update and getattr(update, "message", None):
            await update.message.reply_text("An unexpected error occurred. The team has been notified.")
    except Exception:
        logger.exception("Failed to send error message to user.")
