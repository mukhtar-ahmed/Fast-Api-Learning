from typing import Annotated, Sequence
from fastapi import Depends,HTTPException,status
from app.auth.services.user_service import get_current_user
from sqlalchemy.orm import Session
from .core.database import SessionLocal
from app.auth.models.user import RoleEnum,Role


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
current_user_dp = Annotated[dict,Depends(get_current_user)]
db_session_dp = Annotated[Session,Depends(get_db)]

def require_roles(allowed_roles:Sequence[RoleEnum]):
    """
    Dependency to ensure the current user has the required role.
    Raises 401 if not authenticated, 403 if not authorized.
    """
    def dependency(current_user:current_user_dp, db:db_session_dp):
        if not all([current_user.get('id'),current_user.get('email'),current_user.get('role_id')]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED User')
        role = db.query(Role).filter(Role.id == current_user.get("role_id")).first()
        if role is None or role.name not in [r.value for r in allowed_roles]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden Access")
        return current_user
    return Depends(dependency)