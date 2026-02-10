# handlers/quiz_handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
import os
import json

logger = logging.getLogger("ChurchBot.quiz_handlers")

# Try to load a large question bank from data/quiz_questions.json if present.
DATA_FILE = os.path.join(os.getenv("DATA_DIR", "data"), "quiz_questions.json")
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            QUIZ_QUESTIONS = json.load(f)
    except Exception:
        logger.exception("Failed to load quiz_questions.json; falling back to defaults.")
        QUIZ_QUESTIONS = []
else:
    # Minimal default questions (A-D choices)
    QUIZ_QUESTIONS = [
        {
            "question": "Who created the heavens and the earth?",
            "choices": ["A. Moses", "B. Abraham", "C. God", "D. David"],
            "answer": "C"
        },
        {
            "question": "Who built the ark?",
            "choices": ["A. Noah", "B. Moses", "C. Abraham", "D. Jacob"],
            "answer": "A"
        }
    ]

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not QUIZ_QUESTIONS:
        await update.message.reply_text("No quiz questions available.")
        return
    context.user_data["quiz_index"] = 0
    context.user_data["score"] = 0
    await send_question(update, context, 0)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, idx: int):
    q = QUIZ_QUESTIONS[idx]
    # Build keyboard from choices list (assumes 4 choices)
    keyboard = []
    labels = ["A", "B", "C", "D"]
    for i, choice in enumerate(q.get("choices", [])):
        label = labels[i] if i < len(labels) else str(i)
        keyboard.append([InlineKeyboardButton(choice, callback_data=label)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    # If called from callback, edit or send new message accordingly
    if update.callback_query:
        await update.callback_query.message.reply_text(q["question"], reply_markup=reply_markup)
    else:
        await update.message.reply_text(q["question"], reply_markup=reply_markup)

async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = context.user_data.get("quiz_index", 0)
    if idx >= len(QUIZ_QUESTIONS):
        await query.edit_message_text("Quiz already finished.")
        return
    q = QUIZ_QUESTIONS[idx]
    choice = query.data
    correct = q.get("answer")
    if choice == correct:
        context.user_data["score"] = context.user_data.get("score", 0) + 1
        feedback = f"✅ Correct! You chose {choice}."
    else:
        feedback = f"❌ Wrong. You chose {choice}. Correct: {correct}"
    try:
        await query.edit_message_text(text=feedback)
    except Exception:
        logger.exception("Failed to edit message for feedback.")

    # Next question
    idx += 1
    context.user_data["quiz_index"] = idx
    if idx < len(QUIZ_QUESTIONS):
        # Send next question
        await send_question(update, context, idx)
    else:
        score = context.user_data.get("score", 0)
        total = len(QUIZ_QUESTIONS)
        await query.message.reply_text(f"🎯 Quiz finished! Score: {score}/{total}")
        # Clear quiz state
        context.user_data.pop("quiz_index", None)
        context.user_data.pop("score", None)
