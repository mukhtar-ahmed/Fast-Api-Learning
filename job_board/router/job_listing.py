from typing import Annotated,Optional
from fastapi import APIRouter,Depends,HTTPException,status
from models import Job,Role,User,Application
from pydantic import BaseModel,Field
from .auth import get_current_user,db_session_dep
from sqlalchemy.exc import SQLAlchemyError
from logger import logger

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

class JobIn(BaseModel):
    title:str = Field(min_length=3)
    description:str

class UpdateJob(BaseModel):
    title:Optional[str] = None
    description:Optional[str] = None

class JobOut(BaseModel):
    id: int
    title: str
    description: str
    company_id: int

    class Config:
        orm_mode = True


current_user = Annotated[dict, Depends(get_current_user)]

# All jobs of this company
@router.get("/")
async def all_jobs(current_user:current_user, db:db_session_dep):
    user_role = current_user.get('role')
    company_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, company_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.company.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    jobs = db.query(Job).filter(Job.company_id == company_id).all()
    return {
        'total':len(jobs),
        'data':jobs
    }


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=JobOut)
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

@router.put("/{id}")
async def update_job(current_user:current_user, db:db_session_dep, job_data:UpdateJob,id:int):
    user_role = current_user.get('role')
    company_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, company_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.company.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    job = db.query(Job).filter(Job.company_id == company_id).filter(Job.id == id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job/ Access not found")
    update = False
    if job_data.title:
        job.title = job_data.title
        update = True
    if job_data.description:
        job.description = job_data.description
        update = True
    
    if not update:
        return {
            "message":"Job not updated"
        }
    try:
        db.commit()
        db.refresh(job)
        return {
            'message':"updated siccessfully",
            'data':job
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error While updating")
    
@router.delete("/{id}")
async def delete_job(current_user:current_user, db:db_session_dep,id:int):
    user_role = current_user.get('role')
    company_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, company_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.company.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    job = db.query(Job).filter(Job.company_id == company_id).filter(Job.id == id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job/ Access not found")
    try:
        db.delete(job)
        db.commit()
        return {
            'message':'Job delete'
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error While deleting")
    
@router.get("/{id}/applications")
async def job_applications(current_user:current_user, db:db_session_dep,id:int):
    user_role = current_user.get('role')
    company_id = current_user.get("user_id")
    email = current_user.get("email")
    
    if not all([user_role, company_id, email]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User UNAUTHORIZED")
    if user_role != Role.company.value:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Not has premission")
    # Job -> Applications
    # find Job
    # applications = db.query(Application).filter(Job.company_id == company_id).filter(Job.id == id).filter(Application.job_id == Job.id).all()
    # # find applications on that job
    # # applications = db.query(Application).filter(Application.job_id == job.id).all()
    # return applications
    # Check if the job exists and belongs to the current company
    job = db.query(Job).filter(Job.id == id, Job.company_id == company_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not owned by the company")

    # Get applications for the job
    applications = db.query(Application).filter(Application.job_id == id).all()
    
    return applications
    