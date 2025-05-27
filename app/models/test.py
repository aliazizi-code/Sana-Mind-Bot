from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import validates
from enum import Enum
from .base import Base
from utils.time_zone import get_iran_time


class TestType(Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"


class Test(Base):
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    description = Column(Text(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    test_type = Column(
        String(20), 
        nullable=False, 
        default=TestType.SINGLE_CHOICE.value,
        index=True
    )
    created_at = Column(DateTime, default=lambda: get_iran_time(), nullable=False)
    
    def __repr__(self):
        return (
            f"<Test(id={self.id}, "
            f"title='{self.title}', "
            f"type={self.test_type}, >"
        )
    
    @validates('title')
    def validate_title(self, key, title):
        if len(title.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        return title
    
    @validates('test_type')
    def validate_test_type(self, key, test_type):
        if test_type not in [t.value for t in TestType]:
            raise ValueError(f"Invalid test type. Allowed values: {[t.value for t in TestType]}")
        return test_type
    
    @validates('description')
    def validate_description(self, key, description):
        if description and len(description) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        return description
