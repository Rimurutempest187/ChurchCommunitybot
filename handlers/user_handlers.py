# handlers/user_handlers.py
import os
import json
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.translate_utils import translate_auto

logger = logging.getLogger("ChurchBot.user_handlers")

DATA_DIR = os.getenv("DATA_DIR", "data")
PRAYERS_FILE = os.path.join(DATA_DIR, "prayers.json")
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def load_data(file):
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.exception("Failed to load %s", file)
        return []


def save_data(file, data):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Failed to save %s", file)


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Church Community Bot!\n")


# Command list
async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/verse\n/prayer <text>\n/prayerlist\n/events\n/daily_inspiration\n/myid\n/chatid\n/tran\n\n"
        )


# Verse of the day
async def verse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📖 Today's verse: John 3:16\n")


# Prayer request
async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🙏 Please share your prayer request.\n")
        return
    prayers = load_data(PRAYERS_FILE)
    request = " ".join(context.args)
    prayers.append({"user": update.effective_user.id, "text": request})
    save_data(PRAYERS_FILE, prayers)
    await update.message.reply_text("✅ Prayer request added.\n")


# Prayer list
async def prayerlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prayers = load_data(PRAYERS_FILE)
    if not prayers:
        await update.message.reply_text("🙏 Prayer list is empty.\n")
    else:
        text = "🙏 Prayer Requests:\n"
        for p in prayers:
            text += f"- {p['text']} (User {p['user']})\n"
        await update.message.reply_text(text)


# Events
async def events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = load_data(EVENTS_FILE)
    if not events:
        await update.message.reply_text("📅 No upcoming events.\n")
    else:
        text = "📅 Upcoming Events:\n" + "\n".join(events)
        await update.message.reply_text(text)


# Daily inspiration
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Daily inspiration: Keep the faith strong!\n")


# User ID
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your user ID: {update.effective_user.id}")


# Chat ID
async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")


# Translation command (supports direct text or reply)
async def tran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = None
    text = None

    # Case 1: reply to a message
    if update.message.reply_to_message and update.message.reply_to_message.text:
        text = update.message.reply_to_message.text
        if context.args and len(context.args[-1]) <= 3:
            target = context.args[-1]

    # Case 2: direct text
    elif context.args:
        if len(context.args) > 1 and len(context.args[-1]) <= 3:
            target = context.args[-1]
            text = " ".join(context.args[:-1])
        else:
            text = " ".join(context.args)

    if not text:
        await update.message.reply_text("⚠️ ဘာသာပြန်လိုတဲ့ စာသားကို ထည့်ပါ။\nUsage: /tran <text> [target_lang] or reply to a message with /tran")
        return

    try:
        translated = translate_auto(text, target)
        await update.message.reply_text(f"🌐 Translation:\nOriginal: {text}\nTranslated: {translated}")
    except Exception as e:
        logger.exception("Translation failed: %s", e)
        await update.message.reply_text("❌ Translation failed.\nဘာသာပြန်မအောင်မြင်ပါ။")


# Track user (save to users.json)
async def track_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "NoUsername"
    users = load_data(USERS_FILE)
    if user_id not in users:
        users.append(user_id)
        save_data(USERS_FILE, users)
        logger.info("Tracked new user %s (%s)", user_id, username)
    else:
        logger.debug("User %s (%s) already tracked", user_id, username)
