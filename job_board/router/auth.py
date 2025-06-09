from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,status
from database import SessionLocal
from sqlalchemy.orm import session
from models import User
from pydantic import BaseModel,EmailStr,Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import JWTError, jwt
from config import Settings

settings = Settings()

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
password_hash = CryptContext(schemes=["bcrypt"],deprecated='auto')
db_session_dep = Annotated[session, Depends(get_db)]

def hash_password(password:str):
    return password_hash.hash(password)

def verify_password(signin_password:str, db_password:str):
    return password_hash.verify(signin_password,db_password)
        
class UserIn(BaseModel):
    name:str = Field(min_length=3)
    email:EmailStr
    password:str = Field(min_length=8)
    role:str = Field(default="candidate")
    
    model_config ={
        'json_schema_extra':{
            'example':{
                'name':'Mukhtar',
                'email':"mukhtar@gmail.com",
                'password':'12345678',
                'role':'candidate'
            }
        }
    }

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        orm_mode = True

def create_jwt(id:int, email:str, role:str, exp:timedelta):
    payload = {
        'user_id':id,
        'email':email,
        'role':role,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + exp
    }
    return jwt.encode(payload,settings.secret_key,algorithm=settings.algorithm)

oAuth2_password_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login_user")
def get_current_user(token: Annotated[str, Depends(oAuth2_password_bearer)]):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")

        if not all([user_id, email, role]):
            raise ValueError

        return {
            "user_id": user_id,
            "email": email,
            "role": role
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
@router.post("/create_user",response_model=UserOut, status_code= status.HTTP_201_CREATED)
async def register_user(db:db_session_dep ,user_data:UserIn):
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exist")
    new_user = User(
        name= user_data.name,
        email= user_data.email,
        hashed_password = hash_password(password=user_data.password),
        role = user_data.role
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error {e}")
    
@router.post("/login_user")
async def signin(db:db_session_dep, login_form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    db_user = db.query(User).filter(User.email == login_form.username).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found")
    if not verify_password(signin_password=login_form.password,db_password=db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found")
    token = create_jwt(id=db_user.id,email=db_user.email,role=db_user.role,exp=timedelta(minutes=30))
    return {
        'token_type':"bearer",
        'access_token':token
    }