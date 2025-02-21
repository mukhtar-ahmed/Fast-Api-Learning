from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True,index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)

class Story(Base):
    __tablename__ = 'story'
    
    id = Column(Integer, primary_key=True,index=True)
    day_name = Column(String)
    description = Column(String)
    intresting = Column(Integer)
    new_version = Column(Boolean , default=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    
    
    