from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from fastapi import APIRouter , Depends , HTTPException ,Path
from models import Todos
from database import  SessionLocal
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

class TodoIn(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0,lt=6)
    complete:bool
        
@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@router.get('/todos/{todo_id}')
async def read_todo_by_id(db: db_dependency, todo_id:int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo:TodoIn):
    todo_obj = Todos(**todo.model_dump())
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
    
@router.put('/todo/{id}', status_code=status.HTTP_200_OK)
async def update_todo(db: db_dependency,todo:TodoIn, id:int = Path(gt=0)):
    todo_obj = db.query(Todos).filter(Todos.id == id).first()
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
        
@router.delete('/todo/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id:int=Path(gt=0)):
    todo_obj = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_obj is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail='Todo Not Found')
    else:
        db.delete(todo_obj)
        try:
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error Deleting todo")
        
            