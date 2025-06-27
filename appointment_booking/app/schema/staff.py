from pydantic import BaseModel, Field
from app.schema.user import UserOut
from app.schema.role import RoleOut

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
    
class StaffOut(BaseModel):
    id: int
    bio: str
    user: UserOut
    role: RoleOut
    
