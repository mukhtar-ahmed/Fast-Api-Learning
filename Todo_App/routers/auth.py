from typing import Annotated
from starlette import status
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from models import Users
from database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from passlib.context import CryptContext



router = APIRouter()

class UserIn(BaseModel):
    email:str = Field(min_length=3)
    username:str =Field(min_length=3)
    first_name:str=Field(min_length=3)
    last_name:str=Field(min_length=3)
    password:str=Field(min_length=8)
    role:str
    
    model_config= {
        "json_schema_extra":{
            "example":{
                "email":"user@example.com",
                "username":"user123",
                "first_name":"John",
                "last_name":"Doe",
                "password":"password123",
                "role":"admin"  
            }
        }
    }
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

@router.post('/auth',status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency ,user:UserIn):
    user = Users(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=bcrypt_context.hash( user.password),
        role=user.role
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Error While adding user')
    return user
    
    