from typing import Annotated
from app.models.user import User
from app.schema.user import UserIn
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException,status,Depends
from app.logging.logger import logger
from app.auth.hashing import hash_password,verify_hash
from datetime import timedelta,datetime,timezone
from jose import jwt,ExpiredSignatureError,JWTError
from config import settings
from fastapi.security import OAuth2PasswordBearer

def create_access_token(id:int, email:str,role_id:int,exp:timedelta):
    payload = {
        'id':id,
        'email':email,
        'role_id':role_id,
        'exp':datetime.now(timezone.utc) + exp
    }
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
def get_current_user(token:Annotated[dict,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token=token,key=settings.SECRET_KEY,algorithms=settings.ALGORITHM)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    id = payload.get("id")
    email = payload.get("email")
    role_id = payload.get("role_id")
    exp= payload.get("exp")
    if id is None or email is None or role_id is None or exp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    
    return {
        'id':id,'email':email,'role_id':role_id, 'exp':datetime.fromtimestamp(exp, tz=timezone.utc)
    }
    
db_session_dp = Annotated[dict,Depends(get_current_user)]
def create_user_service(db:Session,payload:UserIn):
    db_user = db.query(User).filter(User.email == payload.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User Already Exist")
    new_user = User(
        full_name = payload.full_name,
        email = payload.email,
        hashed_password = hash_password(payload.password),
        role_id= payload.role_id
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError as e:
        logger.error(f"Error While adding user ;{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error while adding new user")
    
def login_user_service(db:Session, email:str,password:str):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User Not Exist")
    if not verify_hash(password=password,db_password=db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorect Password')
    token = create_access_token(id=db_user.id,email=db_user.email,role_id=db_user.role_id ,exp=timedelta(minutes=180))
    return {
        'token_type':"bearer",
        'access_token':token
    }
