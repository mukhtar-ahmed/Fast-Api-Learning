from fastapi import APIRouter, HTTPException,status
from app.dependencies import current_user_dp,db_session_dp
from app.auth.models.user import Role,RoleEnum, User, StaffProfile, WorkingHour
from app.auth.schema.user import UserOut, StaffOut, RoleOut, StaffIn, WorkingHourIn
from sqlalchemy.exc import SQLAlchemyError
from app.logging.logger import logger

router = APIRouter(
    prefix='/staff',
    tags=['Staff']
)

@router.get("/profile",status_code=status.HTTP_200_OK,response_model=StaffOut)
async def get_staff(current_user:current_user_dp,db:db_session_dp):
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    role_id = current_user.get('role_id')
    if not all([user_id,user_email,role_id]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED User')
    # Check Current user has staff role
    user_role = db.query(Role).filter(Role.id == role_id).first()
    if user_role is None or user_role.name != RoleEnum.staff.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not have required permission")
    
    user_data = db.query(User).filter(User.email == user_email).first()
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        
    staff_data = db.query(StaffProfile).filter(StaffProfile.user_id == user_id).first()
    if staff_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Staff profile not found")
    
    return StaffOut(
        id=staff_data.id,
        bio=staff_data.bio,
        user=UserOut.model_validate(user_data),
        role=RoleOut(id=user_role.id, name=user_role.name)
        
    )
    
@router.put("/profile",status_code=status.HTTP_200_OK,response_model=StaffOut)
async def update_staff(current_user:current_user_dp,db:db_session_dp,bio:str):
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    role_id = current_user.get('role_id')
    if not all([user_id,user_email,role_id]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED User')
    # Check Current user has staff role
    user_role = db.query(Role).filter(Role.id == role_id).first()
    if user_role is None or user_role.name != RoleEnum.staff.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not have required permission")
    
    user_data = db.query(User).filter(User.email == user_email).first()
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        
    staff_data = db.query(StaffProfile).filter(StaffProfile.user_id == user_id).first()
    if staff_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Staff profile not found")
    
    staff_data.bio = bio
    db.commit()
    db.refresh(staff_data)
    
    return StaffOut(
        id=staff_data.id,
        bio=staff_data.bio,
        user=UserOut.model_validate(user_data),
        role=RoleOut(id=user_role.id, name=user_role.name)
        
    )
    
@router.post('/create_working_hours')
async def create_working_hours(current_user:current_user_dp,db:db_session_dp,working_hours:WorkingHourIn):
    # Check if user is Staff
    role = db.query(Role).filter(Role.id == current_user.get("role_id")).first()
    if role is None or role.name != RoleEnum.staff.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access") 
    # check if user is staff
    db_staff:StaffProfile = db.query(StaffProfile).filter(StaffProfile.user_id == working_hours.staff_id).first() # 3
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff profile not found")
    try:
        for entry in working_hours.schedule:
            # existing_day =  db.query(WorkingHour).filter(WorkingHour.day_of_week.casefold() == entry.day_of_week.casefold())
            existing_day = db.query(WorkingHour).filter(WorkingHour.staff_id == db_staff.id,WorkingHour.day_of_week.ilike(entry.day_of_week)).first()
            if existing_day:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Working day already exist")
            wh = WorkingHour(
                staff_id=db_staff.id,
                day_of_week=entry.day_of_week,
                start_time=entry.start_time,
                end_time=entry.end_time
            )
            db.add(wh)
        db.commit()
        return {"message": "Working hours added"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while adding : {e}")
    
@router.get('/get_working_hours')
async def get_working_hours(current_user:current_user_dp,db:db_session_dp):
    role = db.query(Role).filter(Role.id == current_user.get("role_id")).first()
    if role is None or role.name != RoleEnum.staff.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access") 
    # check if user is staff
    db_staff:StaffProfile = db.query(StaffProfile).filter(StaffProfile.user_id == current_user.get("id")).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff profile not found")
    db_staff_working_hours = db.query(WorkingHour).filter(WorkingHour.staff_id == db_staff.id).all()
    if db_staff_working_hours is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Working hours not found")
    return {
        'message': 'Staff Working hours featched',
        'data':db_staff_working_hours
    }