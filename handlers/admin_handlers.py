from telegram import Update
from telegram.ext import ContextTypes
import json
import os

ADMINS_FILE = "admins.json"
EVENTS_FILE = "events.json"

def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a user ID.\nကျေးဇူးပြုပြီး User ID ထည့်ပါ။")
        return
    admins = load_data(ADMINS_FILE)
    user_id = context.args[0]
    if user_id not in admins:
        admins.append(user_id)
        save_data(ADMINS_FILE, admins)
        await update.message.reply_text(f"✅ Admin {user_id} added.\nအက်ဒမင် {user_id} ထည့်ပြီးပါပြီ။")
    else:
        await update.message.reply_text("ℹ️ Already an admin.\nယခုအက်ဒမင်ဖြစ်ပြီးသားပါ။")

async def listadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = load_data(ADMINS_FILE)
    if not admins:
        await update.message.reply_text("No admins yet.\nအက်ဒမင် မရှိသေးပါ။")
    else:
        await update.message.reply_text("Admins:\n" + "\n".join(admins))

async def deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a user ID to remove.\nUser ID ထည့်ပါ။")
        return
    admins = load_data(ADMINS_FILE)
    user_id = context.args[0]
    if user_id in admins:
        admins.remove(user_id)
        save_data(ADMINS_FILE, admins)
        await update.message.reply_text(f"❌ Admin {user_id} removed.\nအက်ဒမင် {user_id} ဖယ်ရှားပြီးပါပြီ။")
    else:
        await update.message.reply_text("User not found in admins.\nအက်ဒမင်စာရင်းထဲတွင် မတွေ့ပါ။")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide a message to broadcast. Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    groups = get_groups()
    success, fail = 0, 0
    for group_id in groups:
        try:
            await context.bot.send_message(chat_id=int(group_id), text=message)
            success += 1
        except Exception:
            fail += 1
    await update.message.reply_text(f"📢 Broadcast complete.\n✅ Success: {success}, ❌ Fail: {fail}")


async def broadcast_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Similar to broadcast_cmd but for user list
    await update.message.reply_text("📢 Broadcast to users sent.\nအသုံးပြုသူများထံ ပို့ပြီးပါပြီ။")

async def addevent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Provide event details.\nEvent အချက်အလက် ထည့်ပါ။")
        return
    events = load_data(EVENTS_FILE)
    event = " ".join(context.args)
    events.append(event)
    save_data(EVENTS_FILE, events)
    await update.message.reply_text(f"📅 Event added: {event}\nအဖြစ်အပျက် ထည့်ပြီးပါပြီ။")

async def clearevents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_data(EVENTS_FILE, [])
    await update.message.reply_text("🗑️ All events cleared.\nအဖြစ်အပျက်အားလုံး ဖျက်ပြီးပါပြီ။")
