from typing import Annotated
from fastapi import APIRouter, Depends
from app.auth.services.user_service import get_current_user
router = APIRouter(
    prefix='/todo',
    tags=['Todo']
)

@router.get('/')
async def todo(current: Annotated[dict,Depends(get_current_user)]):
    return 'abc'