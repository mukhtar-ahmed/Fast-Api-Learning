from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException,status,Query
from sqlalchemy.orm import session
from .user import get_current_user,get_db
from models import Todo
from sqlalchemy.exc import IntegrityError,SQLAlchemyError

router = APIRouter(
    prefix='/todo',
    tags=['Todo']
)
db_user = Annotated[str,Depends(get_current_user)]
db_dependency = Annotated[session, Depends(get_db)]

@router.post('/create_todo',status_code=status.HTTP_201_CREATED)
async def add_todo(db:db_dependency, user:db_user,title:str = Query(min_length=3)):
    new_todo = Todo(title = title,owner_id = user['id']) 
    try:
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
    except IntegrityError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Failed to create user due to integrity error.")
    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal server error occurred.")
    return new_todo
    
