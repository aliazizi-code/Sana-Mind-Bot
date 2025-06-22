import os
import logging
from bot.utils.logger_config import setup_logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from bot.registry import handlers


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    logger.info("Starting the bot...")
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    
    app.add_handlers(handlers)
    
    logger.info("Bot is polling.")
    app.run_polling()


if __name__ == "__main__":
    main()
