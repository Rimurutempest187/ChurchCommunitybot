from telegram import Update
from telegram.ext import ContextTypes

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Admin added.")

async def listadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Admins: none yet.")

async def deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Admin removed.")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Broadcast sent.")

async def broadcast_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Broadcast to users sent.")

async def addevent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Event added.")

async def clearevents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Events cleared.")
