from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

QUIZ_QUESTIONS = [
    {
        "question": "📖 What is the first book of the Bible?",
        "options": {
            "A": "Genesis",
            "B": "Exodus",
            "C": "Leviticus",
            "D": "Numbers"
        },
        "answer": "A"
    },
    {
        "question": "🙏 Who led the Israelites out of Egypt?",
        "options": {
            "A": "David",
            "B": "Moses",
            "C": "Abraham",
            "D": "Joshua"
        },
        "answer": "B"
    }
]

# Start quiz
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["quiz_index"] = 0
    context.user_data["score"] = 0
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data["quiz_index"]
    q = QUIZ_QUESTIONS[idx]

    keyboard = [
        [InlineKeyboardButton(f"A) {q['options']['A']}", callback_data="A")],
        [InlineKeyboardButton(f"B) {q['options']['B']}", callback_data="B")],
        [InlineKeyboardButton(f"C) {q['options']['C']}", callback_data="C")],
        [InlineKeyboardButton(f"D) {q['options']['D']}", callback_data="D")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(q["question"], reply_markup=reply_markup)

# Handle button clicks
async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    idx = context.user_data.get("quiz_index", 0)
    q = QUIZ_QUESTIONS[idx]
    choice = query.data

    if choice == q["answer"]:
        context.user_data["score"] += 1
        feedback = f"✅ Correct! You chose {choice}.\nမှန်ကန်ပါသည်။ {choice} ကိုရွေးခဲ့သည်။"
    else:
        feedback = f"❌ Wrong. You chose {choice}.\nမမှန်ပါ။ {choice} ကိုရွေးခဲ့သည်။"

    await query.edit_message_text(text=feedback)

    # Move to next question
    context.user_data["quiz_index"] += 1
    if context.user_data["quiz_index"] < len(QUIZ_QUESTIONS):
        await send_question(update, context)
    else:
        score = context.user_data["score"]
        total = len(QUIZ_QUESTIONS)
        await query.message.reply_text(
            f"🎯 Quiz finished!\nScore: {score}/{total}\n"
            f"အမှတ်: {score}/{total}"
        )
