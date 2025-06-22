import logging
from bot.utils.logger_config import setup_logging
from bot.handlers.start import start
from bot.handlers.manager import create_test_handler
from bot.handlers.test import (
    show_result,
    show_test,
    delete_test_progress,
    start_test,
    handle_answer,
)
from bot.utils.test_list_func import test_list
from telegram.ext import CommandHandler, CallbackQueryHandler


logger = logging.getLogger(__name__)
logger.info("Registering command and callback query handlers...")


handlers = [
    # Command Handlers
    CommandHandler("start", start),
    CommandHandler("test", test_list),
    create_test_handler,
    
    
    # Callback Query Handlers
    CallbackQueryHandler(show_test, pattern=r"^show_test:\d+$"),
    CallbackQueryHandler(delete_test_progress, pattern=r"^delete_test:\d+$"),
    CallbackQueryHandler(show_result, pattern=r"^show_result:\d+$"),
    CallbackQueryHandler(start_test, pattern=r"^start_test:\d+$"),
    CallbackQueryHandler(handle_answer, pattern=r"^answer:\d+:\d+:\d+$"),  
]

logger.info("Handlers registered successfully.")
