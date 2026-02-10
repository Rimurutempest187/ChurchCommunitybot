from telegram import Update
from telegram.ext import ContextTypes
import json
import os

PRAYERS_FILE = "prayers.json"
EVENTS_FILE = "events.json"

def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to ChurchBot!\nကျောင်းဘော့ထဲကို ကြိုဆိုပါတယ်။")

# Command list
async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/verse\n/prayer\n/prayerlist\n/events\n/daily_inspiration\n/myid\n/chatid\n/tran\n\n"
        "အသုံးပြုနိုင်သော အမိန့်များ:"
    )

# Verse of the day
async def verse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📖 Today's verse: John 3:16\nယနေ့ကျမ်းချက်: ယောဟန် ၃:၁၆")

# Prayer request
async def prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🙏 Please share your prayer request.\nသင့်ဆုတောင်းချက်ကို မျှဝေပါ။")
        return
    prayers = load_data(PRAYERS_FILE)
    request = " ".join(context.args)
    prayers.append({"user": update.effective_user.id, "text": request})
    save_data(PRAYERS_FILE, prayers)
    await update.message.reply_text("✅ Prayer request added.\nဆုတောင်းချက် ထည့်ပြီးပါပြီ။")

# Prayer list
async def prayerlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prayers = load_data(PRAYERS_FILE)
    if not prayers:
        await update.message.reply_text("🙏 Prayer list is empty.\nဆုတောင်းစာရင်း မရှိသေးပါ။")
    else:
        text = "🙏 Prayer Requests:\n"
        for p in prayers:
            text += f"- {p['text']} (User {p['user']})\n"
        await update.message.reply_text(text)

# Events
async def events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = load_data(EVENTS_FILE)
    if not events:
        await update.message.reply_text("📅 No upcoming events.\nအဖြစ်အပျက် မရှိသေးပါ။")
    else:
        text = "📅 Upcoming Events:\n" + "\n".join(events)
        await update.message.reply_text(text)

# Daily inspiration
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Daily inspiration: Keep the faith strong!\nယနေ့ အားပေးစကား: ယုံကြည်ခြင်းကို ခိုင်မာစေပါ။")

# User ID
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your user ID: {update.effective_user.id}")

# Chat ID
async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

# Translation placeholder
async def tran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 Translation feature coming soon.\nဘာသာပြန်ခြင်း လုပ်ဆောင်ချက် မကြာမီ ရနိုင်မည်။")

# Track user (logging only)
async def track_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "NoUsername"
    print(f"Tracking user {user_id} ({username})")
    await update.message.reply_text("👤 User tracked.\nအသုံးပြုသူကို မှတ်သားပြီးပါပြီ။")
