import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from bot.bot_messages import add_test_instruction, add_question_instruction
from bot.utils.auth import is_admin
from db.crud.create_test import create_test_from_text
from db.crud.add_questions import add_questions_from_text


logger = logging.getLogger(__name__)

WAITING_FOR_TEST, ADDING_QUESTIONS = range(2)

async def create_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User {user.id} - {user.full_name} called /create_test")
    
    if not await is_admin(update):
        logger.warning(f"Unauthorized access to /create_test by user {user.id} - {user.full_name}")
        return ConversationHandler.END
    
    await update.message.reply_text(add_test_instruction, parse_mode="Markdown")
    logger.info(f"Sent add_test_instruction to user {user.id} - {user.full_name}")
    return WAITING_FOR_TEST

async def receive_test_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Received test text from user {user.id} - {user.full_name}")
    result_create_test = create_test_from_text(update.message.text)
    if result_create_test["err"]:
        logger.warning(f"Test creation failed for user {user.id} - {user.full_name}: {result_create_test['result']}")
        await update.message.reply_text(result_create_test['result'])
        await update.message.reply_text("دوباره تلاش کنید.")
        return WAITING_FOR_TEST
    logger.info(f"Test created successfully for user {user.id} - {user.full_name}: {result_create_test['test_id']}")
        
    await update.message.reply_text(result_create_test['result'])
    context.user_data['test_id'] = result_create_test['test_id']
    await update.message.reply_text(add_question_instruction)
    return ADDING_QUESTIONS
    
async def receive_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    test_id = context.user_data.get('test_id')
    logger.info(f"Received question text from user {user.id} - {user.full_name} for test {test_id}")
    
    if not test_id:
        logger.error(f"Test ID not found for user {user.id} - {user.full_name}")
        await update.message.reply_text("خطایی رخ داد لطفا مجددا تلاش کنید.")
        return ADDING_QUESTIONS
    
    try:
        result_add_questions = add_questions_from_text(text, test_id)
    except Exception:
        logger.exception(f"Error while adding questions for user {user.id} - {user.full_name} for test {test_id}")
        await update.message.reply_text("خطایی رخ داد لطفا مجددا تلاش کنید.")
        return ADDING_QUESTIONS
    
    logger.info(f"Questions added for test_id {test_id} by user {user.id} - {user.full_name}")
    await update.message.reply_text(f"{result_add_questions}\n\nدر صورت اتمام دستور /finish را ارسال کنید یا ادامه دهید.")
    return ADDING_QUESTIONS

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User {user.id} - {user.full_name} finished creating test process")
    await update.message.reply_text("عملیات پایان یافت.")
    return ConversationHandler.END

create_test_handler = ConversationHandler(
    entry_points=[CommandHandler('create_test', create_test)],
    states={
        WAITING_FOR_TEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_test_text)],
        ADDING_QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question_text)],
    },
    fallbacks=[CommandHandler('finish', finish)]
)
