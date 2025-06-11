from typing import Annotated
from fastapi import APIRouter,Depends
from sqlalchemy.orm import session
from app.dependencies import get_db
from app.models.user import User

router = APIRouter(
    tags=['Auth'],
    prefix='/auth'
)

@router.get("/")
async def get_user(db: Annotated[session,Depends(get_db)]):
    users = db.query(User).all()
    return users