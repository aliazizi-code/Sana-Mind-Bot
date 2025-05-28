from sqlalchemy import String, Column, Integer
from db.base import Base


class BotSetting(Base):
    __tablename__ = 'bot_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
