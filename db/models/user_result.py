from sqlalchemy import Column, Integer, ForeignKey, Text
from db.base import Base


class UserResult(Base):
    __tablename__ = 'user_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    result_text = Column(Text, nullable=False)

    def __repr__(self):
        return (
            f"<UserResult(id={self.id}, "
            f"user_id={self.user_id}, "
            f"test_id={self.test_id}, "
            f"result_text={self.result_text[:20]}...>"
        )
