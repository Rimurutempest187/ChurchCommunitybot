# handlers/admin_handlers.py
import os
import json
import logging
from functools import wraps
from typing import Callable, Any

from telegram import Update
from telegram.ext import ContextTypes

from utils.bot_utils import add_admin, get_admins, remove_admin, add_event, clear_events, get_groups, is_admin

logger = logging.getLogger("ChurchBot.admin_handlers")

DATA_DIR = os.getenv("DATA_DIR", "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


# --- Users persistence helpers ---
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


# --- Admin-only decorator ---
def admin_only(func: Callable[..., Any]):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return
        if not is_admin(user.id):
            try:
                await update.message.reply_text("⛔ You are not authorized to use this command.")
            except Exception:
                logger.debug("Could not send unauthorized message.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


# --- Admin management ---
@admin_only
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a user ID. Usage: /addadmin <user_id>")
        return
    user_id = context.args[0]
    if add_admin(user_id):
        await update.message.reply_text(f"✅ Admin {user_id} added.")
    else:
        await update.message.reply_text("ℹ️ Already an admin.")


@admin_only
async def listadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = get_admins()
    if not admins:
        await update.message.reply_text("No admins yet.")
    else:
        await update.message.reply_text("Admins:\n" + "\n".join(admins))


@admin_only
async def deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a user ID to remove. Usage: /deladmin <user_id>")
        return
    user_id = context.args[0]
    if remove_admin(user_id):
        await update.message.reply_text(f"❌ Admin {user_id} removed.")
    else:
        await update.message.reply_text("User not found in admins.")


# --- Broadcast to groups (uses get_groups from utils.bot_utils) ---
@admin_only
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a message to broadcast. Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    groups = get_groups()
    if not groups:
        await update.message.reply_text("ℹ️ No groups registered to broadcast to.")
        return

    success, fail = 0, 0
    for group_id in groups:
        try:
            await context.bot.send_message(chat_id=int(group_id), text=message)
            success += 1
        except Exception as e:
            logger.exception("Failed to send broadcast to group %s: %s", group_id, e)
            fail += 1

    await update.message.reply_text(f"📢 Broadcast complete.\n✅ Success: {success}, ❌ Fail: {fail}")


# --- Broadcast to tracked users (users.json) ---
@admin_only
async def broadcast_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a message to broadcast. Usage: /broadcast_users <message>")
        return
    message = " ".join(context.args)
    users = load_users()
    if not users:
        await update.message.reply_text("ℹ️ No users tracked for broadcasting.")
        return

    success, fail = 0, 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=message)
            success += 1
        except Exception as e:
            logger.exception("Failed to send broadcast to user %s: %s", user_id, e)
            fail += 1

    await update.message.reply_text(f"📢 User broadcast complete.\n✅ Success: {success}, ❌ Fail: {fail}")


# --- Events management ---
@admin_only
async def addevent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide event details. Usage: /addevent <event text>")
        return
    event = " ".join(context.args)
    try:
        add_event(event)
        await update.message.reply_text(f"📅 Event added: {event}")
    except Exception:
        logger.exception("Failed to add event.")
        await update.message.reply_text("❌ Failed to add event.")


@admin_only
async def clearevents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        clear_events()
        await update.message.reply_text("🗑️ All events cleared.")
    except Exception:
        logger.exception("Failed to clear events.")
        await update.message.reply_text("❌ Failed to clear events.")
