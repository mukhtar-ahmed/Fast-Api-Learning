from typing import Annotated
from fastapi import APIRouter,Depends, HTTPException,status
from .auth import db_session_dep, get_current_user
from models import Role,User,Job,Application

router = APIRouter(
    tags=["Admin"],
    prefix="/admin"
)
current_user = Annotated[dict, Depends(get_current_user)]

@router.get("/users")
async def get_all_user(current_user:current_user,db:db_session_dep):
    user_role = current_user.get('role')
    company_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, company_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.admin.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    users = db.query(User).all()
    return {
        "total":len(users),
        "data":users
    }
    
@router.get("/jobs")
async def get_all_jobs(current_user:current_user,db:db_session_dep):
    user_role = current_user.get('role')
    company_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, company_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.admin.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    users = db.query(Job).all()
    return {
        "total":len(users),
        "data":users
    }

@router.get("/applications")
async def get_all_applications(current_user:current_user,db:db_session_dep):
    user_role = current_user.get('role')
    company_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, company_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.admin.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    application = db.query(Application).all()
    return {
        "total":len(application),
        "data":application
    }