# handlers/group_handlers.py
import os
import json
import logging
from typing import List

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger("ChurchBot.group_handlers")

DATA_DIR = os.getenv("DATA_DIR", "data")
GROUPS_FILE = os.path.join(DATA_DIR, "groups.json")


def _ensure_data_dir() -> None:
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception:
        logger.exception("Failed to ensure data directory %s", DATA_DIR)


def load_groups() -> List[str]:
    _ensure_data_dir()
    if not os.path.exists(GROUPS_FILE):
        return []
    try:
        with open(GROUPS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(x) for x in data]
            return []
    except Exception:
        logger.exception("Failed to load groups.json; returning empty list.")
        return []


def save_groups(groups: List[str]) -> None:
    _ensure_data_dir()
    try:
        with open(GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(groups, f, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Failed to save groups.json")


async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ Provide a group ID.\nUsage: /addgroup <group_id>")
        return
    group_id = str(context.args[0])
    groups = load_groups()
    if group_id not in groups:
        groups.append(group_id)
        save_groups(groups)
        await update.message.reply_text(f"✅ Group {group_id} added.\nGroup {group_id} ထည့်ပြီးပါပြီ။")
        logger.info("Group %s added by user %s", group_id, update.effective_user.id if update.effective_user else "unknown")
    else:
        await update.message.reply_text("ℹ️ Already in group list.\nGroup စာရင်းထဲတွင် ရှိပြီးသားပါ။")


async def listgroups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    groups = load_groups()
    if not groups:
        await update.message.reply_text("No groups yet.\nGroup မရှိသေးပါ။")
    else:
        await update.message.reply_text("Groups:\n" + "\n".join(groups))


async def delgroup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ Provide a group ID to remove.\nUsage: /delgroup <group_id>")
        return
    group_id = str(context.args[0])
    groups = load_groups()
    if group_id in groups:
        groups.remove(group_id)
        save_groups(groups)
        await update.message.reply_text(f"❌ Group {group_id} removed.\nGroup {group_id} ဖယ်ရှားပြီးပါပြီ။")
        logger.info("Group %s removed by user %s", group_id, update.effective_user.id if update.effective_user else "unknown")
    else:
        await update.message.reply_text("Group not found.\nGroup မတွေ့ပါ။")


async def on_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle my_chat_member updates. Auto-register the chat when the bot becomes a member/administrator,
    and remove it when the bot is kicked or leaves.
    """
    my_chat_member = getattr(update, "my_chat_member", None)
    if my_chat_member is None:
        logger.debug("on_my_chat_member called without my_chat_member payload.")
        return

    chat = my_chat_member.chat
    old_member = my_chat_member.old_chat_member
    new_member = my_chat_member.new_chat_member

    old_status = getattr(old_member, "status", "unknown")
    new_status = getattr(new_member, "status", "unknown")
    chat_id_str = str(chat.id)

    # When bot is added or promoted to admin/member -> register group
    if new_status in ("administrator", "member"):
        groups = load_groups()
        if chat_id_str not in groups:
            groups.append(chat_id_str)
            save_groups(groups)
            try:
                await context.bot.send_message(chat.id, "✅ Group registered automatically.")
            except Exception:
                logger.exception("Failed to send registration confirmation to chat %s", chat.id)
            logger.info("Auto-registered group %s (new_status=%s)", chat.id, new_status)

    # When bot is kicked or left -> remove group
    elif new_status in ("kicked", "left"):
        groups = load_groups()
        if chat_id_str in groups:
            groups.remove(chat_id_str)
            save_groups(groups)
            logger.info("Removed group %s after bot left or was kicked (new_status=%s)", chat.id, new_status)

    logger.debug(
        "my_chat_member update: chat=%s (%s) old_status=%s new_status=%s",
        chat.title or chat.id,
        chat.id,
        old_status,
        new_status,
    )
