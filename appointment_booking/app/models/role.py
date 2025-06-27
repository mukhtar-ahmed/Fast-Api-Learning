from app.core.database import Base
from sqlalchemy import Column, Integer, Enum as saEnum
from enum import Enum

class RoleEnum(str,Enum):
    admin='admin'
    staff='staff'
    client='client'
    
class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer,primary_key=True,index=True, nullable=False)
    name = Column(saEnum(RoleEnum,create_type=True),nullable=False,index=True,unique=True)