from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import validates, relationship
from db.base import Base
from bot.utils.time_zone import get_iran_time


class Test(Base):
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: get_iran_time(), nullable=False)
    
    questions = relationship(
        "Question",
        back_populates='test',
        order_by='Question.order',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        return (
            f"<Test(id={self.id}, "
            f"title='{self.title}', "
        )
    
    @validates('title')
    def validate_title(self, key, title):
        if len(title.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return title
    
    @validates('description')
    def validate_description(self, key, description):
        if description and len(description) > 1000:
            raise ValueError("Description cannot exceed 500 characters")
        return description
