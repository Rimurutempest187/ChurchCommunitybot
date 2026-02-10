from telegram import Update
from telegram.ext import ContextTypes
import json
import os

GROUPS_FILE = "groups.json"

def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return []
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_groups(groups):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a group ID.\nGroup ID ထည့်ပါ။")
        return
    groups = load_groups()
    group_id = context.args[0]
    if group_id not in groups:
        groups.append(group_id)
        save_groups(groups)
        await update.message.reply_text(f"✅ Group {group_id} added.\nGroup {group_id} ထည့်ပြီးပါပြီ။")
    else:
        await update.message.reply_text("ℹ️ Already in group list.\nGroup စာရင်းထဲတွင် ရှိပြီးသားပါ။")

async def listgroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = load_groups()
    if not groups:
        await update.message.reply_text("No groups yet.\nGroup မရှိသေးပါ။")
    else:
        await update.message.reply_text("Groups:\n" + "\n".join(groups))

async def delgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a group ID to remove.\nGroup ID ထည့်ပါ။")
        return
    groups = load_groups()
    group_id = context.args[0]
    if group_id in groups:
        groups.remove(group_id)
        save_groups(groups)
        await update.message.reply_text(f"❌ Group {group_id} removed.\nGroup {group_id} ဖယ်ရှားပြီးပါပြီ။")
    else:
        await update.message.reply_text("Group not found.\nGroup မတွေ့ပါ။")

async def on_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.my_chat_member.chat
    new_status = update.my_chat_member.new_chat_member.status
    old_status = update.my_chat_member.old_chat_member.status

    msg = (
        f"🔄 Chat member update:\n"
        f"Chat: {chat.title or chat.id}\n"
        f"Old status: {old_status}\n"
        f"New status: {new_status}\n\n"
        f"👥 Group update received.\nGroup အခြေအနေ ပြောင်းလဲမှု ရရှိခဲ့ပါသည်။"
    )
    await update.message.reply_text(msg)

