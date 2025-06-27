from typing import Annotated,List
from pydantic import BaseModel,constr
from datetime import time

class DayWorkingHour(BaseModel):
    day_of_week: Annotated[str, constr(strip_whitespace=True)]
    start_time: time
    end_time: time

class WorkingHourIn(BaseModel):
    staff_id:int
    schedule: List[DayWorkingHour]