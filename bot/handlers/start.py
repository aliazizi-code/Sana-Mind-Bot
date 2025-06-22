import logging
from utils.logger_config import setup_logging
from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from db.session import SessionLocal
from db.models.user import User
from bot.bot_messages import start_msg, error_msg
from bot.utils.auth import is_admin
from bot.utils.test_list_func import test_list


logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    user = update.effective_user
    
    try:
        exiting_user = db.query(User).filter(User.telegram_id == user.id).first()
        
        if not exiting_user:
            logger.info(f"New user detected. Adding user {user.id} - {user.full_name} to database.")
            new_user = User(telegram_id=user.id, full_name=user.full_name)
            db.add(new_user)
            db.commit()
        else:
            logger.info(f"Existing user found: {user.id} - {user.full_name}")
        
        await update.message.reply_text(start_msg)
    
    except Exception as e:
        logger.exception(f"Error in /start handler for user {user.id}: {e}")
        await update.message.reply_text(error_msg)
        db.rollback()
    
    finally:
        admin = await is_admin(update)
        commands = [
            BotCommand("test", "لیست تست‌ها"),
        ]
            
        if admin:
            logger.info(f"User {user.id} is admin. Adding admin commands.")
            commands.extend([
                BotCommand("create_test", "ایجاد تست‌ها"),
            ])
        else:
            logger.info(f"User {user.id} is not admin")
        
        await context.bot.set_my_commands(commands)
        logger.info(f"Commands set for user {user.id}")
        await test_list(update, context)
    