from typing import Annotated
from fastapi import APIRouter,Depends
from app.schema.role import RoleIn
from app.schema.user import UserIn,UserOut
from app.auth.service import create_user_service,login_user_service
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import db_session_dp,current_user_dp

router = APIRouter(
    tags=['Auth'],
    prefix='/auth'
)

@router.post("/signup",response_model=UserOut)
async def create_user(db:db_session_dp ,payload:UserIn):
    return create_user_service(db=db,payload=payload)
    
@router.post('/login')
async def login_user(db:db_session_dp,login_data:Annotated[OAuth2PasswordRequestForm,Depends()]):
    return login_user_service(db=db,email=login_data.username,password=login_data.password)

