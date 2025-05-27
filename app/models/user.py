from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .base import Base
from datetime import datetime 


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, full_name='{self.full_name}', username='{self.username}', is_admin={self.is_admin}, is_active={self.is_active}, is_banned={self.is_banned})>"

    def __str__(self):
        return f"User(telegram_id={self.telegram_id}, full_name={self.full_name})"
    
    def __init__(self, telegram_id, full_name: str, username=None, is_admin=False, is_active=True, is_banned=False):
        self.telegram_id = telegram_id
        self.full_name = full_name
        self.username = username
        self.is_admin = is_admin
        self.is_active = is_active
        self.is_banned = is_banned
