import logging
from utils.logger_config import setup_logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.session import SessionLocal
from db.models.test import Test
from bot.bot_messages import test_menu_msg, no_tests_msg


logger = logging.getLogger(__name__)


async def test_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"User {update.effective_user.id} requested test list")
        db = SessionLocal()
        logger.debug("Database session opened")

        # Query all available tests
        tests = db.query(Test).all()
        logger.debug(f"Found {len(tests)} tests in database")

        if not tests:
            logger.warning("No tests available in database")
            await update.message.reply_text(no_tests_msg)
            return

        # Log test titles for debugging
        test_titles = [test.title for test in tests]
        logger.debug(f"Available tests: {', '.join(test_titles)}")

        # Prepare keyboard
        keyboard = [
            [InlineKeyboardButton(test.title, callback_data=f"show_test:{test.id}")]
            for test in tests
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        logger.debug("Test menu keyboard prepared")

        # Send message with test list
        await update.message.reply_text(
            test_menu_msg,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        logger.info(f"Test list sent successfully to user {update.effective_user.id}")

    except Exception as e:
        logger.error(f"Error in test_list: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "خطایی در دریافت لیست آزمون‌ها رخ داد. لطفاً مجدداً تلاش کنید."
        )
    finally:
        db.close()
        logger.debug("Database session closed")
