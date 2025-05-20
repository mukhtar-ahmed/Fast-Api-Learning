from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    tags=["Auth"],
    prefix="/auth"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session,Depends(get_db)]
hash_password = CryptContext(schemes=["bcrypt"],deprecated='auto')
SECRET_KEY = 'ITSSECRET'
ALGORITH = 'HS256'

class UserIn(BaseModel):
    name:str = Field(min_length=3)
    email:str = Field(min_length=3)
    password:str = Field(min_length=6)
    
    model_config = {
        "json_schema_extra":{
            "example":{
                'name':'Mukhtar',
                'email':'mukhtar@abc.com',
                "password":"123456"
            }
        }
    }
    
def create_access_token(id:int, email:str, timedata:timedelta):
    encode = {
        "id":id,
        "email":email
    }
    expires = datetime.now(timezone.utc) + timedata
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY, algorithm=ALGORITH)

def get_current_user():
    pass

@router.post("/add")
async def create_user(user:UserIn, db: db_dependency):
    new_user = User(
        name = user.name,
        email = user.email,
        password = hash_password.encrypt(user.password)
    )
    
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        token = create_access_token(id=new_user.id,email=new_user.email,timedata=timedelta(minutes=30))
        print(token)
    except Exception:
        db.rollback
    return {
        'data': new_user,
        'token': token
    }
    
    
@router.post("/login")
async def login_user(db:db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = db.query(User).filter(User.email == form_data.username).first()
    if user is None:
        return {
            "User not found"
        }
    token = create_access_token(id=user.id,email=user.email,timedata=timedelta(minutes=30))
    return {
        'data': user,
        "token":token
    }