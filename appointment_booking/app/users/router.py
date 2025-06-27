from fastapi import APIRouter,HTTPException,status
from app.dependencies import db_session_dp,current_user_dp
from app.models.role import Role,RoleEnum
from app.models.staff_profile import StaffProfile
from app.models.user import User
from app.schema.user import UserListOut,UserOut
from app.schema.role import RoleOut
from app.schema.staff import StaffIn,StaffOut
from sqlalchemy.exc import SQLAlchemyError
from app.logging.logger import logger

router = APIRouter(
    prefix='/users',
    tags=[
        'Users'
    ]
)

@router.get('/', response_model=UserListOut, status_code=status.HTTP_200_OK)
async def get_users(current_user:current_user_dp, db:db_session_dp):
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    role_id = current_user.get('role_id')
    if user_id is None or user_email is None or role_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED User')
    user_role = db.query(Role).filter(Role.id == role_id).first()
    if user_role is None or user_role.name != RoleEnum.admin.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not have required permission")
    users = db.query(User).all()
    user_data = [UserOut.model_validate(user) for user in users]
    return {
        'total': len(user_data),
        'data': user_data
    }

@router.get('/staff', status_code=status.HTTP_200_OK)
async def get_staff(current_user:current_user_dp,db:db_session_dp):
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    role_id = current_user.get('role_id')
    if user_id is None or user_email is None or role_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED User')
    user_role = db.query(Role).filter(Role.id == role_id).first()
    if user_role is None or user_role.name != RoleEnum.admin.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not have required permission")
    # Staff role not found
    staff_role = db.query(Role).filter(Role.name == RoleEnum.staff.value).first()
    if staff_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff Role not found")
    # Find All user with Staff Role
    staff_users = db.query(User).filter(User.role_id == staff_role.id).all()
    staff_data = [UserOut.model_validate(user) for user in staff_users]
    return {
        "total": len(staff_data),
        "data": staff_data
    }

@router.get('/client', status_code=status.HTTP_200_OK)
async def get_staff(current_user:current_user_dp,db:db_session_dp):
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    role_id = current_user.get('role_id')
    if user_id is None or user_email is None or role_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED User')
    user_role = db.query(Role).filter(Role.id == role_id).first()
    if user_role is None or user_role.name != RoleEnum.admin.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not have required permission")
    # Client role not found
    staff_role = db.query(Role).filter(Role.name == RoleEnum.client.value).first()
    if staff_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff Role not found")
    # Find All user with Client Role
    client_users = db.query(User).filter(User.role_id == staff_role.id).all()
    client_data = [UserOut.model_validate(client) for client in client_users]
    return {
        "total": len(client_data),
        "data": client_data
    }
    
@router.get('/{id}',response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user(current_user:current_user_dp, db:db_session_dp,id:int):
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    role_id = current_user.get('role_id')
    if user_id is None or user_email is None or role_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED User')
    user_role = db.query(Role).filter(Role.id == role_id).first()
    if user_role is None or user_role.name != RoleEnum.admin.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not have required permission")
    user = db.query(User).filter(User.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Under Not found")
    return UserOut.model_validate(user)
        
    
@router.post('/staff',response_model=StaffOut,status_code=status.HTTP_201_CREATED)
async def create_staff(current_user:current_user_dp,db:db_session_dp,staff:StaffIn):
    role = db.query(Role).filter(Role.id == current_user.get("role_id")).first()
    if role is None or role.name != RoleEnum.admin.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    db_user = db.query(User).filter(User.id == staff.user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User Not found')
    db_user_role = db.query(Role).filter(Role.id == db_user.role_id).first()
    if db_user_role is None or db_user_role.name != RoleEnum.staff.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User is not a staff member')
    db_staff = db.query(StaffProfile).filter(StaffProfile.user_id == db_user.id).first()
    if db_staff is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Staff already exist')
    new_staff_profile = StaffProfile(**staff.model_dump())
    try:
        db.add(new_staff_profile)
        db.commit()
        db.refresh(new_staff_profile)
        role_out = RoleOut(
            id=db_user_role.id,
            name=db_user_role.name
        )
        user_out = UserOut(
            id=new_staff_profile.user.id,
            full_name=new_staff_profile.user.full_name,
            email=new_staff_profile.user.email,
            role_id=new_staff_profile.user.role_id,
            is_active=new_staff_profile.user.is_active,
            created_at=new_staff_profile.user.created_at,
            updated_at=new_staff_profile.user.updated_at
        )
        
        return StaffOut(
            id=new_staff_profile.id,
            bio=new_staff_profile.bio,
            user=user_out,
            role=role_out
        )
    
    except SQLAlchemyError as e:
        db.rollback(new_staff_profile)
        logger.error(f"Error while creating staff: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error while creating staff: {e}" )
    
