from typing import List, Annotated
from pydantic import BaseModel, EmailStr, Field,constr
from app.auth.models.user import RoleEnum
from datetime import datetime,time

class RoleIn(BaseModel):
    name:RoleEnum 
    
    model_config = {
        'json_schema_extra': {
            "example": {
                "name": "client",
            }
        }
    }
class RoleOut(BaseModel):
    id:int
    name:str

class UserIn(BaseModel):
    full_name:str = Field(..., min_length=3)
    email:EmailStr
    password:str = Field(..., min_length=8)
    role_id: int
    
    model_config = {
        'json_schema_extra': {
            "example": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "password": "strongpassword123",
                "role_id": 1
            }
        }
    }
    
class UserOut(BaseModel):
    id:int
    full_name:str 
    email:EmailStr
    is_active : bool
    created_at: datetime
    updated_at: datetime
    
    model_config= {
        "from_attributes":True
    }

class UserListOut(BaseModel):
    total:int
    data:list[UserOut]
    
class StaffOut(BaseModel):
    id: int
    bio: str
    user: UserOut
    role: RoleOut
    
class StaffIn(BaseModel):
    user_id: int = Field(...)
    bio: str = Field(..., min_length=3)
    
    model_config = {
        'json_schema_extra':{
            'example':{
                'user_id':1,
                'bio':'its doctor'
            }
        }
    }

class DayWorkingHour(BaseModel):
    day_of_week: Annotated[str, constr(strip_whitespace=True)]
    start_time: time
    end_time: time

class WorkingHourIn(BaseModel):
    staff_id:int
    schedule: List[DayWorkingHour]
    
