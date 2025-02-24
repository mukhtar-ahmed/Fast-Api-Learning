from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Todos, Users
from .auth import get_current_user, SECRET_KEY, ALGORITHM
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from pydantic import BaseModel


router = APIRouter(
    prefix="/user",
    tags=["User"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
db_user = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

class UserVerification(BaseModel):
    current_password: str
    new_password: str
    
    model_config={
        "json_schema_extra":{
            "example":{
                "current_password": "password123",
                "new_password": "newpassword123"
            }
        }
    }
        
@router.get('')
async def get_user(user: db_user, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(Users).filter(Users.id == user.get('id')).first()
        


@router.post("/change_password")
async def change_password(user: db_user, db:db_dependency, verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(verification.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current Password is not correct")
    hashed_password = bcrypt_context.hash(verification.new_password)
    current_user.hashed_password = hashed_password
    try:
        db.commit()
        db.refresh(current_user)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {"message": "Password Changed Successfully"}
        