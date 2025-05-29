from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base


class Option(Base):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    text = Column(String(255), nullable=False)
    
    question = relationship("Question", back_populates="options")

    def __repr__(self):
        return f"<Option(id={self.id}, text='{self.text[:20]}...')>"
