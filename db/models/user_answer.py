from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import validates
from db.base import Base


class UserAnswer(Base):
    __tablename__ = 'user_answers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    selected_option_id = Column(Integer, ForeignKey('options.id'), nullable=False)
    rank = Column(Integer, nullable=True)
    
    @validates('rank')
    def validate_rank(self, key, rank):
        if rank is not None and rank not in {1, 2}:
            raise ValueError("Rank must be either 1 or 2")
        return rank
    
