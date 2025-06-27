from app.core.database import Base
from sqlalchemy import Column,Integer, ForeignKey,String
from sqlalchemy.orm import relationship

class StaffProfile(Base):
    __tablename__ = 'staff_profiles'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'),nullable=False,unique=True)
    bio = Column(String, nullable=False)
    
    user = relationship('User',back_populates='staff_profile')
    working_hours = relationship('WorkingHour', back_populates='staff')
    services = relationship('Service',back_populates='staff')
    
    appointments = relationship('Appointment', back_populates='staff') 