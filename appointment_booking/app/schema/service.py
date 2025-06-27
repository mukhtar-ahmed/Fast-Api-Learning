from pydantic import BaseModel, Field

class ServiceIn(BaseModel):
    name:str = Field(..., min_length=3)
    description:str = Field(..., min_length=10)
    duration_minutes:int

class ServiceOut(BaseModel):
    id: int
    name: str
    description: str
    duration_minutes: int
    staff_id: int
    
    model_config= {
        "from_attributes":True
    }
    
    