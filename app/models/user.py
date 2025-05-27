from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .base import Base
from utils.time_zone import get_iran_time


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    username = Column(String, nullable=True, index=True)
    is_admin = Column(Boolean, default=False, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_banned = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: get_iran_time(), nullable=False)
    
    def __repr__(self):
        return (
            f"<User(id={self.id}, "
            f"telegram_id={self.telegram_id}, "
            f"full_name='{self.full_name}', "
            f"username='{self.username}', "
            f"is_admin={self.is_admin}, "
            f"is_active={self.is_active}, "
            f"is_banned={self.is_banned})> "
        )
