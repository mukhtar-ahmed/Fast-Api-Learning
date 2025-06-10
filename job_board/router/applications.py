from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,status
from .auth import get_current_user,db_session_dep
from models import Role, Application
router = APIRouter(
    prefix="/applications"
    ,
    tags=["Applications"]
)
current_user = Annotated[dict,Depends(get_current_user)]
@router.post("/jobs/{id}")
async def apply_job(current_user:current_user, db:db_session_dep, details:str,id:int):
    user_role = current_user.get('role')
    candidate_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, candidate_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.candidate.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    new_application = Application(
        user_id = candidate_id,
        job_id = id,
        details = details
    )
    try:
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        return new_application
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error {e}")
    
@router.get("")
async def user_applications(current_user:current_user, db:db_session_dep):
    user_role = current_user.get('role')
    candidate_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, candidate_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.candidate.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    
    return db.query(Application).filter(Application.user_id == candidate_id).all()