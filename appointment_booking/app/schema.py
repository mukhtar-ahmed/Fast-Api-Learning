from typing import Optional
from pydantic import BaseModel

class APIResponse(BaseModel):
    message:str
    data:Optional[any] = None