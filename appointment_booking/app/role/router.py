from fastapi import APIRouter,status
from app.dependencies import db_session_dp
from app.schema.role import RoleIn
from app.schema.api_response import APIResponse
from app.models.role import RoleEnum
from app.dependencies import require_roles
from app.role.services import create_db_role,get_all_roles

router = APIRouter(
    prefix='/roles',
    tags=['Roles']
)

@router.post('',status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def create_role(db:db_session_dp,role_data:RoleIn): 
    return create_db_role(db=db,role_data=role_data)

@router.get('', status_code=status.HTTP_200_OK, response_model=APIResponse)
async def get_roles(db:db_session_dp, current_user:dict = require_roles([RoleEnum.admin,RoleEnum.staff,RoleEnum.client])):
    return get_all_roles(current_user=current_user,db=db)
    