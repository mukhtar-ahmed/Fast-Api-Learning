from typing import Annotated
from app.auth.models.user import User,StaffProfile,WorkingHour
from app.auth.schema.user import UserIn,RoleIn,StaffIn,StaffOut,UserOut,RoleOut,WorkingHourIn
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException,status,Depends
from app.logging.logger import logger
from app.auth.utils.hashing import hash_password,verify_hash
from datetime import timedelta,datetime,timezone
from jose import jwt,ExpiredSignatureError,JWTError
from config import settings
from fastapi.security import OAuth2PasswordBearer
from app.auth.models.user import Role,RoleEnum

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
    
def create_user_role( db:Session,role_data:RoleIn): # current_user:dict,
    # check if role is admin
    # role = db.query(Role).filter(Role.id == current_user.get("role_id")).first()
    # if role is None or role.name != RoleEnum.admin.value:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    # db_role = db.query(Role).filter(Role.name == role_data.name).first()
    # print(f"db_role: {db_role}")
    # print(f"role_data: {role_data.name}")
    # if db_role:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Role already exist")
    new_role = Role(**role_data.model_dump())
    try:
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return new_role
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error while adding role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error While adding new role"
        )

def get_all_roles(current_user:dict, db:Session):
    role = db.query(Role).filter(Role.id == current_user.get("role_id")).first()
    if role is None or role.name != RoleEnum.admin.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    roles = db.query(Role).all()
    return {
        'total':len(roles),
        'data':roles
    }


# def create_staff_working_hours(current_user=dict, db=Session, working_hours=WorkingHourIn):
#     # Check if user is admin
#     role = db.query(Role).filter(Role.id == current_user.get("role_id")).first()
#     if role is None or role.name != RoleEnum.admin.value:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access") 
#     # check if user is staff
#     db_staff:StaffProfile = db.query(StaffProfile).filter(StaffProfile.user_id == working_hours.staff_id).first() # 3
#     if not db_staff:
#         raise HTTPException(status_code=404, detail="Staff profile not found")
#     print("::::::::::::::::::::::::::::::::::::::::")
#     print(db_staff.user_id)
#     print(db_staff.id)
#     # print()
#     print(len(working_hours.schedule)) # list
#     print("::::::::::::::::::::::::::::::::::::::::")
#     try:
#         for entry in working_hours.schedule:
#             # existing_day =  db.query(WorkingHour).filter(WorkingHour.day_of_week.casefold() == entry.day_of_week.casefold())
#             existing_day = db.query(WorkingHour).filter(WorkingHour.staff_id == db_staff.id,WorkingHour.day_of_week.ilike(entry.day_of_week)).first()
#             if existing_day:
#                 raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Working day already exist")
#             wh = WorkingHour(
#                 staff_id=db_staff.id,
#                 day_of_week=entry.day_of_week,
#                 start_time=entry.start_time,
#                 end_time=entry.end_time
#             )
#             db.add(wh)
#         db.commit()
#         return {"message": "Working hours added"}
#     except SQLAlchemyError as e:
#         db.rollback()
#         logger.error(e)
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while adding : {e}")
    
# def get_staff_working_hours(current_user=dict, db=Session, id=int):
#     role = db.query(Role).filter(Role.id == current_user.get("role_id")).first()
#     if role is None or role.name != RoleEnum.admin.value:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access") 
#     # check if user is staff
#     db_staff:StaffProfile = db.query(StaffProfile).filter(StaffProfile.user_id == id).first()
#     if not db_staff:
#         raise HTTPException(status_code=404, detail="Staff profile not found")
#     db_staff_working_hours = db.query(WorkingHour).filter(WorkingHour.staff_id == db_staff.id).all()
#     if db_staff_working_hours is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Working hours not found")
#     return {
#         'message': 'Staff Working hours featched',
#         'data':db_staff_working_hours
#     }