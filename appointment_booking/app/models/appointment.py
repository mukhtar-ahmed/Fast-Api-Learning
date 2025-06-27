from app.core.database import Base
from sqlalchemy import Column,Integer, ForeignKey,String, DateTime
from sqlalchemy.orm import relationship

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