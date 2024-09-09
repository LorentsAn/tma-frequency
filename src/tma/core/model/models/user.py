from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from tma.core.database import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint('session_id', name='unique_session_id'),
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, session_id='{self.session_id}')>"
