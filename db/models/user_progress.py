from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.base import Base
from utils.time_zone import get_iran_time


class UserProgress(Base):
    __tablename__ = 'user_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    current_order = Column(Integer, default=1)
    last_taken_date = Column(DateTime, default=lambda: get_iran_time())
    
    test = relationship("Test")
    answers = relationship(
        "UserAnswer",
        back_populates='progress',
        cascade='all, delete-orphan'
    )
