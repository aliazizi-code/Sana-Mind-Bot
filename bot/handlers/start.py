from telegram import Update
from telegram.ext import ContextTypes
from db.session import SessionLocal
from db.crud.message import get_message_by_key
from db.models.user import User

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    msg = get_message_by_key(db, 'start', default="سلام. چقدر خودتو میشناسی؟")
    user = update.effective_user
    
    try:
        exiting_user = db.query(User).filter(User.telegram_id == user.id).first()
        
        if not exiting_user:
            new_user = User(telegram_id=user.id, full_name=user.full_name)
            db.add(new_user)
            db.commit()
        
        await update.message.reply_text(msg)
    
    except Exception as e:
        await update.message.reply_text("مشکلی پیش آمده است")
        print(e)
        db.rollback()
    
    finally:
        db.close()
    