from app.core.database import Base
from sqlalchemy import Column,Integer, ForeignKey,String, DateTime,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime,timezone

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer,primary_key=True,index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True,index=True)
    hashed_password = Column(String,nullable=False)
    role_id = Column(Integer,ForeignKey('roles.id'))
    is_active = Column(Boolean, default=True,nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda:datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True, default=lambda:datetime.now(timezone.utc))
    
    staff_profile = relationship('StaffProfile',back_populates='user')
    appointments = relationship('Appointment', back_populates='client')