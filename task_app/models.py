from datetime import datetime,timezone
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean


class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, index=True, primary_key=True)
    name = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
class Todo(Base):
    __tablename__ = 'todo'
    
    id = Column(Integer,index=True, primary_key=True)
    title = Column(String)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))