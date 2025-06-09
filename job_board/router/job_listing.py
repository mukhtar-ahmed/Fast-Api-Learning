from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException,status
from models import Job,Role
from pydantic import BaseModel,Field
from .auth import get_current_user,db_session_dep
from sqlalchemy.exc import SQLAlchemyError
from logger import logger

router = APIRouter(
    prefix="/job",
    tags=["Job"]
)

class JobIn(BaseModel):
    title:str = Field(min_length=3)
    description:str

class JobOut(BaseModel):
    id: int
    title: str
    description: str
    company_id: int

    class Config:
        orm_mode = True


current_user = Annotated[dict, Depends(get_current_user)]


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=JobOut)
async def add_job(current_user:current_user, job:JobIn, db:db_session_dep):
    user_role = current_user.get('role')
    company_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, company_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.company.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    new_job = Job(
        title = job.title,
        description = job.description,
        company_id = company_id
    )
    try:
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB Error while adding job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error while adding")
    return new_job