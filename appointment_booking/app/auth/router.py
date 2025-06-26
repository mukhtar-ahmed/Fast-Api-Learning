from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import session
from sqlalchemy.exc import SQLAlchemyError
from app.dependencies import get_db
from app.auth.models.user import User
from app.auth.schema.user import UserIn,UserOut,RoleIn,StaffIn,StaffOut,WorkingHourIn
from passlib.context import CryptContext
from app.logging.logger import logger
from app.auth.services.user_service import create_user_service,login_user_service,create_user_role,get_all_roles
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import db_session_dp,current_user_dp

router = APIRouter(
    tags=['Auth'],
    prefix='/auth'
)

# Signup -> admin, staff, client
# Login
# Create Role
# Get Role
# Create Staff -> staff
# Create Working Hours
# Get Staff Working Hours


@router.post("/signup",response_model=UserOut)
async def create_user(db:db_session_dp ,payload:UserIn):
    return create_user_service(db=db,payload=payload)
    
@router.post('/login')
async def login_user(db:db_session_dp,login_data:Annotated[OAuth2PasswordRequestForm,Depends()]):
    return login_user_service(db=db,email=login_data.username,password=login_data.password)

@router.post('/create_role')
async def create_role(db:db_session_dp,role_data:RoleIn): # current_user:current_user_dp,
    return create_user_role(db=db,role_data=role_data) # current_user=current_user,

@router.get('/get_roles')
async def get_roles(current_user:current_user_dp,db:db_session_dp):
    return get_all_roles(current_user=current_user,db=db)



# @router.post('/create_working_hours')
# async def create_working_hours(current_user:current_user_dp,db:db_session_dp,working_hours:WorkingHourIn):
#     return create_staff_working_hours(current_user=current_user, db=db, working_hours=working_hours)

# @router.get('/get_working_hours/{id}')
# async def get_working_hours(current_user:current_user_dp,db:db_session_dp,id:int):
#     return get_staff_working_hours(current_user=current_user, db=db, id=id)
    