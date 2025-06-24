from sqlalchemy import Column, Integer, String, Boolean, DateTime,Enum as saEnum, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.core.database import Base
from enum import Enum
from datetime import datetime,timezone

class RoleEnum(str,Enum):
    admin='admin'
    staff='staff'
    client='client'
    
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
    
    
class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer,primary_key=True,index=True, nullable=False)
    name = Column(saEnum(RoleEnum,create_type=True),nullable=False,index=True,unique=True)
    

class StaffProfile(Base):
    __tablename__ = 'staff_profiles'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'),nullable=False,unique=True)
    bio = Column(String, nullable=False)
    
    user = relationship('User',back_populates='staff_profile')
    working_hours = relationship('WorkingHour', back_populates='staff')
    staff = relationship('StaffProfile','services')
    services = relationship('Service',back_populates='staff')
    
    appointments = relationship('Appointment', back_populates='staff') 

class WorkingHour(Base):
    __tablename__ = 'working_hours'
    
    id = Column(Integer,nullable=False, unique=True,primary_key=True)
    staff_id = Column(Integer,ForeignKey('staff_profiles.id',ondelete='CASCADE'),nullable=False)
    day_of_week = Column(String, nullable=False)
    start_time = Column(Time,nullable=False)
    end_time = Column(Time,nullable=False)
    
    staff = relationship('StaffProfile', back_populates='working_hours')
    
    
class Service(Base):
    __tablename__ = 'services'
    
    id = Column(Integer,nullable=False, unique=True,primary_key=True)
    staff_id = Column(Integer, ForeignKey('staff_profiles.id'),nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    duration_minutes = Column(Integer)
    
    staff = relationship('StaffProfile',back_populates= 'services')
    
class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, nullable=False,unique=True)
    client_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    staff_id = Column(Integer, ForeignKey('staff_profiles.id', ondelete='CASCADE'))
    service_id = Column(Integer, ForeignKey('services.id'))
    appointment_time = Column(DateTime,nullable=False)
    status = Column(String, default='booked')
    
    client = relationship('User', back_populates='appointments')
    staff =  relationship('StaffProfile', back_populates='appointments')
    service = relationship("Service")
    
