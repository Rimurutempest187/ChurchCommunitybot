# handlers/admin_handlers.py
from telegram import Update
from telegram.ext import ContextTypes
from utils.bot_utils import add_admin, get_admins, remove_admin
from handlers.group_handlers import load_groups
import json, os, logging

logger = logging.getLogger("ChurchBot.admin_handlers")

DATA_DIR = os.getenv("DATA_DIR", "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.exception("Failed to load users.json; returning empty list.")
        return []

def save_users(users):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Failed to save users.json")

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a user ID. Usage: /addadmin <user_id>")
        return
    user_id = context.args[0]
    if add_admin(user_id):
        await update.message.reply_text(f"✅ Admin {user_id} added.")
    else:
        await update.message.reply_text("ℹ️ Already an admin.")

async def listadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = get_admins()
    if not admins:
        await update.message.reply_text("No admins yet.")
    else:
        await update.message.reply_text("Admins:\n" + "\n".join(admins))

async def deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a user ID to remove. Usage: /deladmin <user_id>")
        return
    user_id = context.args[0]
    if remove_admin(user_id):
        await update.message.reply_text(f"❌ Admin {user_id} removed.")
    else:
        await update.message.reply_text("User not found in admins.")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a message to broadcast. Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    groups = load_groups()
    success, fail = 0, 0
    for group_id in groups:
        try:
            await context.bot.send_message(chat_id=int(group_id), text=message)
            success += 1
        except Exception as e:
            logger.exception("Failed to send broadcast to group %s: %s", group_id, e)
            fail += 1
    await update.message.reply_text(f"📢 Broadcast complete.\n✅ Success: {success}, ❌ Fail: {fail}")

async def broadcast_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a message to broadcast. Usage: /broadcast_users <message>")
        return
    message = " ".join(context.args)
    users = load_users()
    success, fail = 0, 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=message)
            success += 1
        except Exception as e:
            logger.exception("Failed to send broadcast to user %s: %s", user_id, e)
            fail += 1
    await update.message.reply_text(f"📢 User broadcast complete.\n✅ Success: {success}, ❌ Fail: {fail}")
