from database import Base
from sqlalchemy import Column, DateTime,Integer, String,ForeignKey, Enum as SQLEnum
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from enum import Enum
class Role(str,Enum):
    admin = 'admin'
    company = 'company'
    candidate = 'candidate'


class User(Base):
    __tablename__ ='user'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String,unique=True,index=True,nullable=False)
    hashed_password = Column(String,nullable=False)
    role = Column(SQLEnum(Role),nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    jobs = relationship("Job", back_populates='company')  # Only for company users
    applications = relationship("Application", back_populates="candidate")  # For candidate users
    
    
class Job(Base):
    __tablename__ = "job"
    
    id = Column(Integer, nullable=False, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    company_id = Column(Integer, ForeignKey('user.id'), nullable=False)  # FK to User
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    company = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade='all,delete')
    
class Application(Base):
    __tablename__ = 'application'
    
    id = Column(Integer,nullable=False,index=True,primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job.id", ondelete='CASCADE'),nullable=False)
    details = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
    
    job = relationship("Job", back_populates="applications")
    candidate = relationship("User", back_populates="applications")