from pydantic import BaseModel
from datetime import time,date

class AppointmentIn(BaseModel):
    staff_id:int
    service_id:int
    appointment_time:time
    appointment_date:date
