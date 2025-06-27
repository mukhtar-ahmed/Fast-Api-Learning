from typing import Optional,Any
from pydantic import BaseModel

class APIResponse(BaseModel):
    message:str
    data:Optional[Any] = None