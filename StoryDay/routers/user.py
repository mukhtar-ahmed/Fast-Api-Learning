from typing import Annotated
from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from sqlalchemy.orm import session
from models import User
from .auth import get_current_user
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

def get_db():
    db  = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[session , Depends(get_db)]
db_user = Annotated[str, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    
    model_config = {
        "example":{
            "old_password": "old_password",
            "new_password": "new_password"
        }
    }

@router.get("")
async def read_users(user: db_user, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    return db.query(User).filter(User.id == user.get("id")).first()

@router.post("/change-password")
async def change_password(user: db_user, db: db_dependency, change_password: ChangePassword):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    current_user = db.query(User).filter(User.id == user.get("id")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not bcrypt_context.verify(change_password.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    current_user.hashed_password = bcrypt_context.hash(change_password.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
    
    