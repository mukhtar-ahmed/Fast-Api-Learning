from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

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