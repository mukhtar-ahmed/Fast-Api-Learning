from datetime import datetime, timedelta, timezone
from typing import Annotated
from starlette import status
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from models import Users
from database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt



router = APIRouter()
SECRET_KEY = 'ITSSECRECT'
ALGORITHM = 'HS256'

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

class Token(BaseModel):
    access_token: str
    token_type: str
    
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

def create_access_token(username:str, user_id:int, timedata:timedelta):
    encode = {
        'sub':username,
        'id':user_id
    }
    expires = datetime.now(timezone.utc) + timedata
    encode.update({'exp':expires})
    access_token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return access_token


def authenticate_user(db: db_dependency, email:str,password:str):
    user = db.query(Users).filter(Users.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found')
    else:
        if bcrypt_context.verify(password,user.hashed_password):
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')

        
@router.post('/token', response_model=Token)
async def login_for_access_token(db:db_dependency, form_data : Annotated[OAuth2PasswordRequestForm,Depends()]):
    user = authenticate_user(db=db, email=form_data.username,password=form_data.password)
    access_token = create_access_token(user.username, user.id, timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}
    
        
    
    