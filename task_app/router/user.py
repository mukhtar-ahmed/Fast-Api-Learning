from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from pydantic import BaseModel, EmailStr, Field
from models import User
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt,JWTError
from logger import logger

router = APIRouter(
    tags=['Auth'],
    prefix='/auth'
    )
hash_password = CryptContext(schemes=['bcrypt'],deprecated='auto')
SECRET_KEY = 'ITSSECRET'
ALGORITHM = 'HS256'

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/login')
def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
        user_id:int = payload.get("id")
        email:str = payload.get("email")
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except JWTError:
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "id":user_id,
        "email":email
        }

def create_access_token(id:int, email:str,timedelta:timedelta):
    encode = {
        'id': id,
        "email":"email"
    }
    expires = datetime.now(timezone.utc) + timedelta
    encode.update({
        'exp':expires
    })
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

class UserIn(BaseModel):
    name : str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=8)
    
    model_config = {
        'json_schema_extra':{
            'example':{
                "name":"Mukhtar",
                "email":"mukhtar@gmail.com",
                "password":"12345678"
            }
        }
    }

@router.post('/create_user', status_code=status.HTTP_201_CREATED, summary="Register new user")
async def CreateUser(db:db_dependency, user: UserIn):
    logger.info("Creating user start...")
    existing_user = db.query(User).filter(User.email == user.email).first()
    logger.info("Create User...")
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")
    new_user = User(name=user.name, email=user.email, hashed_password=hash_password.hash(user.password))
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Failed to create user due to integrity error.")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal server error occurred.")
    logger.info("Creating user Finished...")
    return {
        "message": "User created successfully.",
        "data":{
            'id':new_user.id,
            'name':new_user.name,
            'email':new_user.email,
            'is_active':new_user.is_active,
            'created_at':new_user.created_at
        }
        
    }
    
@router.post("/login", status_code=status.HTTP_200_OK,summary="Login user and return jwt")
async def login_user(db:db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    #Lookup user bu email
    user = db.query(User).filter(User.email == form_data.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Verify user password
    if not hash_password.verify(form_data.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    access_token = create_access_token(id=user.id, email=user.email,timedelta=timedelta(minutes=30))
    return {
        "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
    }
    