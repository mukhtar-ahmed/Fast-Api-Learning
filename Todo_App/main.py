from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from fastapi import FastAPI , Depends , HTTPException ,Path
from models import Base, Todos
from database import engine , SessionLocal
from sqlalchemy.exc import SQLAlchemyError


Base.metadata.create_all(bind=engine)
app = FastAPI()

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
        
@app.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@app.get('/todos/{todo_id}')
async def read_todo_by_id(db: db_dependency, todo_id:int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
@app.post("/todo/", status_code=status.HTTP_201_CREATED)
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