from typing import Annotated
from fastapi import Depends
from app.auth.services.user_service import get_current_user
from sqlalchemy.orm import session
from .core.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
current_user_dp = Annotated[dict,Depends(get_current_user)]
db_session_dp = Annotated[session,Depends(get_db)]