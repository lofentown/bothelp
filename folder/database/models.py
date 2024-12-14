from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    username = Column(String, default=None, nullable=True)
    connection_date = Column(DateTime, default=datetime.now, nullable=False)
    tg_id = Column(String, nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    problem_text = Column(String, default=None, nullable=True)

    def __repr__(self):
        return self.tg_id


class BlockedUser(Base):
    __tablename__ = 'BlockedUsers'
    id = Column(Integer, primary_key=True)
    block_count = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return self.block_count