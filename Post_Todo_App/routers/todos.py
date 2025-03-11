from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from fastapi import APIRouter , Depends , HTTPException ,Path
from models import Todos
from database import  SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from .auth import get_current_user

router = APIRouter(
    prefix='/todos'
    ,
    tags=['Todos']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
db_user = Annotated[dict , Depends(get_current_user)]

class TodoIn(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0,lt=6)
    complete:bool
    
    model_config = {
    "json_schema_extra":{
        "example":{
            "title":"Buy milk",
            "description":"Buy milk from store",
            "priority":1,
            "complete":False
        }
    }
}

        
@router.get('', status_code=status.HTTP_200_OK)
async def read_all(user:db_user, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials" )
    return db.query(Todos).filter(Todos.owner_id == user['id']).all()

@router.get('/{todo_id}')
async def read_todo_by_id(user:db_user, db: db_dependency, todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials" )
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user['id']).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
@router.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user:db_user, db: db_dependency, todo:TodoIn):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    todo_obj = Todos(**todo.model_dump(), owner_id=user["id"])
    db.add(todo_obj)
    try:
        db.commit()
        db.refresh(todo_obj)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating todo")
    return {
        'message': 'todo created',
        'data': todo_obj
    }
    
@router.put('/{id}', status_code=status.HTTP_200_OK)
async def update_todo(user: db_user, db: db_dependency,todo:TodoIn, id:int = Path(gt=0)):
    todo_obj = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if todo_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')
    else:
        todo_obj.title = todo.title
        todo_obj.description = todo.description
        todo_obj.priority = todo.priority
        todo_obj.complete = todo.complete
        
        try:
            db.commit()
            db.refresh(todo_obj)
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating todo")
        return {
            'message': 'todo updated',
            'data': todo_obj
        }
        
@router.delete('/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: db_user, db: db_dependency, todo_id:int=Path(gt=0)):
    todo_obj = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_obj is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail='Todo Not Found')
    else:
        db.delete(todo_obj)
        try:
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error Deleting todo")
        
            