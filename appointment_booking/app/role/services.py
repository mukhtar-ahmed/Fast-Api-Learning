from fastapi import HTTPException,status
from app.models.role import Role,RoleEnum
from app.schema.role import RoleIn,RoleOut, RoleListOut
from app.schema.api_response import APIResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session  
from app.logging.logger import logger
from enum import Enum

class ErrorEnum(Enum):
    FAILED_TO_CREATE_Role = "failed_to_create_role"

def create_db_role(db:Session,role_data:RoleIn):
    new_role = Role(**role_data.model_dump())
    try:
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return APIResponse(
            message='Role added successfully',
            data=RoleOut.model_validate(new_role)
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error while adding role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[
                {
                    "message": str(e),
                    "error": [ErrorEnum.FAILED_TO_CREATE_Role.value]
                }
            ],
        )

def get_all_roles(current_user:dict, db:Session):
    roles = db.query(Role).all()
    response_data = RoleListOut(
        total=len(roles),
        roles=[RoleOut.model_validate(role) for role in roles]
    )
    return APIResponse(
        message = "Roles fetched successfully",
        data= response_data.model_dump()
    )