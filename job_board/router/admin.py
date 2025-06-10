from typing import Annotated, Optional
from fastapi import APIRouter,Depends, HTTPException,status
from .auth import db_session_dep, get_current_user,hash_password,admin_required
from models import Role,User,Job,Application
from pydantic import BaseModel, Field
from logger import logger
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(
    tags=["Admin"],
    prefix="/admin"
)

class UserUpdate(BaseModel):
    name:Optional[str] =None
    password:Optional[str] =None
    
    model_config ={
        'json_schema_extra':{
            'example':{
                'name':'Mukhtar',
                'password':'12345678',
            }
        }
    }

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
    model_config = {
        'json_schema_extra':{
            'example':{
                'title':'its job title update',
                'description':'its job description update'
            }
        }
    }

class ApplicationUpdate(BaseModel):
    details: Optional[str] = None
    
    model_config = {
        'json_schema_extra':{
            'example':{
                'details':'Application Details update'
            }
        }
    }
    
CurrentAdmin = Annotated[dict, Depends(admin_required)]
# User CRUD
@router.get("/users")
async def get_users(admin:CurrentAdmin ,db:db_session_dep):
    users = db.query(User).all()
    logger.info(f"Fetched {len(users)} users by admin {admin['email']}")
    return {
        "total":len(users),
        "data":users
    }
  
@router.put('/users/{id}')
async def update_user(admin:CurrentAdmin , db:db_session_dep,id:int,user_data:UserUpdate):
    db_user = db.query(User).filter(User.id == id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user_data.name and len(user_data.name.strip()) >= 3:
        db_user.name = user_data.name.strip()
    if user_data.password and len(user_data.password.strip()) >= 8:
        db_user.hashed_password = hash_password(user_data.password.strip())
    db.commit()
    db.refresh(db_user)
    logger.info(f"User updated successfully ID:{db_user.id}")
    return {
        "message": "User updated successfully",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
        }
    }

@router.delete("/users/{id}")
async def delete_user(admin:CurrentAdmin , db:db_session_dep,id:int):
    db_user = db.query(User).filter(User.id == id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(db_user)
    db.commit()
    logger.info(f"Admin {admin['email']} deleted user ID {db_user.id}")
    return {
        "message": "User Delete successfully",
    }
# Jobs CRUD
@router.get("/jobs")
async def get_jobs(admin:CurrentAdmin ,db:db_session_dep):
    users = db.query(Job).all()
    return {
        "total":len(users),
        "data":users
    }

@router.put("/jobs/{id}")
async def update_job(admin:CurrentAdmin, db:db_session_dep, id:int,job_data:JobUpdate):
    job = db.query(Job).filter(Job.id == id).first()
    if job is None:
        logger.info(f"Admin {admin.get("email")} tried to update non-existent job ID {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    update = False
    if job_data.title:
        job.title = job_data.title
        update = True
    if job_data.description:
        job.description = job_data.description
        update = True
    if not update:
        return {"message": "No changes provided"}
    
    try:
        db.commit()
        db.refresh(job)
        logger.info(f"Admin {admin.get("email")} update the job ID {job.id}")
        return {
            "message": "Job updated successfully",
            "job": {
                "id": job.id,
                "title": job.title,
                "description": job.description
            }
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating job ID:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while updating job")

@router.delete("/jobs/{id}")
async def delete_job(admin:CurrentAdmin, db:db_session_dep, id:int):
    job = db.query(Job).filter(Job.id == id).first()
    if job is None:
        logger.warning(f"Admin {admin.get('email')} try to delete not existing job ID: {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    try:
        db.delete(job)
        db.commit()
        logger.info(f"Job ID {id} deleted by admin {admin.get('email')}")
        return {"message": "Job deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error while deleting job ID:{job.id} Error:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting job")

# Application CRUD
@router.get("/applications")
async def get_applications(admin:CurrentAdmin ,db:db_session_dep):
    application = db.query(Application).all()
    return {
        "total":len(application),
        "data":application
    }

@router.put("/applications/{id}")
async def update_application(admin:CurrentAdmin ,db:db_session_dep,id:int, application_data:ApplicationUpdate):
    application = db.query(Application).filter(Application.id == id).first()
    if application is None:
        logger.warning(f"Admin {admin.get('email')} trying to delete not existing pplication ID {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if application_data.details:
        application.details = application_data.details
        try:
            db.commit()
            db.refresh(application)
            logger.info(f"Application ID:{application.id} updated by Admin {admin.get('email')}")
            return {
                'message':'Application updated successfully',
                'data':{
                    'details':application.details
                }
            }
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating Application ID:{e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while updating job")

@router.delete("/applications/{id}")
async def delete_application(admin:CurrentAdmin ,db:db_session_dep,id:int):
    application = db.query(Application).filter(Application.id == id).first()
    if application is None:
        logger.warning(f"Admin {admin.get('email')} trying to delete not existing pplication ID {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    try:
        db.delete(application)
        db.commit()
        logger.info(f"application ID {id} deleted by admin {admin.get('email')}")
        return {"message": "application deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error while deleting job ID:{application.id} Error:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting job")
    