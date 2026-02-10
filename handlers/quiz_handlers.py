from telegram import Update
from telegram.ext import ContextTypes

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎯 Quiz started.")

async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("✅ Quiz button clicked.")
