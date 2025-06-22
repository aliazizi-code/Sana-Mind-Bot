from sqlalchemy import Column, Integer, ForeignKey, DateTime
from bot.utils.time_zone import get_iran_time
from sqlalchemy.orm import relationship
from db.base import Base


class UserAnswer(Base):
    __tablename__ = 'user_answers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    selected_option_id = Column(Integer, ForeignKey('options.id'), nullable=False)
    answer_at = Column(DateTime, default=lambda: get_iran_time())
    
    progress = relationship("UserProgress", back_populates='answers')
    question = relationship("Question")
    option = relationship("Option")
    
