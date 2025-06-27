from app.core.database import Base
from sqlalchemy import Column,Integer, ForeignKey,String,Time
from sqlalchemy.orm import relationship

class WorkingHour(Base):
    __tablename__ = 'working_hours'
    
    id = Column(Integer,nullable=False, unique=True,primary_key=True)
    staff_id = Column(Integer,ForeignKey('staff_profiles.id',ondelete='CASCADE'),nullable=False)
    day_of_week = Column(String, nullable=False)
    start_time = Column(Time,nullable=False)
    end_time = Column(Time,nullable=False)
    
    staff = relationship('StaffProfile', back_populates='working_hours')