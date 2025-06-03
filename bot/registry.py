from bot.handlers import (
    start,
    test_list, show_test, start_test, handle_answer, delete_test_progress, show_result

)
from telegram.ext import CommandHandler, CallbackQueryHandler


handlers = [
    # Command Handlers
    CommandHandler("start", start),
    CommandHandler("test", test_list),
    
    # Callback Query Handlers
    CallbackQueryHandler(show_test, pattern=r"^show_test:\d+$"),
    CallbackQueryHandler(delete_test_progress, pattern=r"^delete_test:\d+$"),
    CallbackQueryHandler(show_result, pattern=r"^show_result:\d+$"),
    CallbackQueryHandler(start_test, pattern=r"^start_test:\d+$"),
    CallbackQueryHandler(handle_answer, pattern=r"^answer:\d+:\d+:\d+$"),
]
