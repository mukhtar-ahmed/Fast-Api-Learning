from datetime import datetime, timedelta, timezone
from typing import Annotated
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from fastapi import  APIRouter, Depends, Query, Path, HTTPException
from pydantic import BaseModel, Field
from models import User
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from jose import jwt

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')
SECRET_KEY = 'ITSASECRETKEY'
ALGORITHM = 'HS256'

class UserIn(BaseModel):
    first_name:str = Field(min_length=3)
    last_name:str = Field(min_length=3)
    email:str = Field(min_length=3)
    password:str = Field(min_length=8)
    role: str  = Field(min_length=3)
    
    model_config = {
        'json_schema_extra':{
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email":"abc@gmail.com",
                "password": "password123",
                "role": "admin"
            }
        }
    }

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    
def create_access_token(username: str, user_id: int, timedata: timedelta):
    encode = {
        'sub': username,
        'id': user_id
        }
    expires = datetime.now(timezone.utc) + timedata
    encode.update({
        'exp':expires
    })
    return jwt.encode(encode,SECRET_KEY, algorithm=ALGORITHM )
        

@router.post('/create_user', status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, user:UserIn):
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password),
        role=user.role
    )
    check_user =  db.query(User).filter(User.email == user.email).first()
    if check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Error while adding the user')
    access_token = create_access_token(username=new_user.email, user_id=new_user.id, timedata=timedelta(minutes=30))
    return {
                "access_token": access_token,
                "token_type": "bearer",
                "data":{
                    "email": new_user.email,
                    "role": new_user.role,
                    "first_name":new_user.first_name,
                    "last_name":new_user.last_name,
                    "user_id":new_user.id
                    }
                }
    

        
@router.post('/token')
async def login_for_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = db.query(User).filter(User.email == form_data.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    else:
        hashed_password = bcrypt_context.verify(form_data.password, user.hashed_password)
        if not hashed_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Password is not correct')
        else:
            access_token = create_access_token(username=user.email, user_id=user.id, timedata=timedelta(minutes=30))
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "data":{
                    "email": user.email,
                    "role": user.role,
                    "first_name":user.first_name,
                    "last_name":user.last_name,
                    "user_id":user.id
                    }
                }
