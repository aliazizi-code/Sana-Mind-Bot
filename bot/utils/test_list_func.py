from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.session import SessionLocal
from db.models.test import Test
from bot.bot_messages import test_menu_msg, no_tests_msg


async def test_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    tests = db.query(Test).all()
    
    if not tests:
        await update.message.reply_text(no_tests_msg)
        return
    
    keyboard = [
        [InlineKeyboardButton(test.title, callback_data=f"show_test:{test.id}")]
        for test in tests
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        test_menu_msg,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
