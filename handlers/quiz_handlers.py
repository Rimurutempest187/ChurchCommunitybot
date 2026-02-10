from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Start quiz with inline buttons
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("A) Option 1", callback_data="A"),
            InlineKeyboardButton("B) Option 2", callback_data="B"),
        ],
        [
            InlineKeyboardButton("C) Option 3", callback_data="C"),
            InlineKeyboardButton("D) Option 4", callback_data="D"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎯 Quiz started!\nChoose the correct answer:\n\nမြန်မာဘာသာဖြင့်: အဖြေကိုရွေးပါ။",
        reply_markup=reply_markup
    )

# Handle button clicks
async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # acknowledge the click

    choice = query.data
    # Example: mark "B" as correct
    if choice == "B":
        text = "✅ Correct! You chose B.\nမှန်ကန်ပါသည်။ B ကိုရွေးခဲ့သည်။"
    else:
        text = f"❌ Wrong. You clicked {choice}.\nမမှန်ပါ။ {choice} ကိုရွေးခဲ့သည်။"

    await query.edit_message_text(text=text)
