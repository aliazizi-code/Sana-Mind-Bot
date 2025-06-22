from db.session import SessionLocal
from db.models.user import User


async def is_admin(update) -> bool:
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
    db.close()
    
    return user.is_admin
