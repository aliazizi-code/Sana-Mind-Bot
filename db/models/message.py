from sqlalchemy import String, Column, Integer
from db.base import Base


class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
