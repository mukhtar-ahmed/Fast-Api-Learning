from app.core.database import Base
from sqlalchemy import Column,Integer, ForeignKey,String
from sqlalchemy.orm import relationship

class Service(Base):
    __tablename__ = 'services'
    
    id = Column(Integer,nullable=False, unique=True,primary_key=True)
    staff_id = Column(Integer, ForeignKey('staff_profiles.id'),nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    duration_minutes = Column(Integer)
    
    staff = relationship('StaffProfile',back_populates= 'services')