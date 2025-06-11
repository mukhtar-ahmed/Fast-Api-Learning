from sqlalchemy import Column, Integer, String, Boolean
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer,primary_key=True,index=True)
    email = Column(String, nullable=False, unique=True,index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    