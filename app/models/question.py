from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from .base import Base


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    text = Column(String(255), nullable=False)
    
    options = relationship("Option", back_populates="question")

    def __repr__(self):
        return f"<Question(id={self.id}, text='{self.text[:20]}...')>"
    
    @validates('text')
    def validate_text(self, key, text):
        if len(text.strip()) < 5:
            raise ValueError("Question text must be at least 5 characters long")
        return text
