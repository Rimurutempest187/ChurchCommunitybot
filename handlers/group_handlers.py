from telegram import Update
from telegram.ext import ContextTypes

async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Group added.")

async def listgroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Groups: none yet.")

async def delgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Group removed.")

async def on_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chat member update received.")
