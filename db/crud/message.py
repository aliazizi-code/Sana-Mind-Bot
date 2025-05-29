from sqlalchemy.orm import Session
from db.models.message import Message

def get_message_by_key(session: Session, key: str) -> str:
    msg = session.query(Message).filter_by(key=key).first()
    return msg.value if msg else None
