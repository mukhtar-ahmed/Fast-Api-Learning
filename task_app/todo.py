from typing import Annotated
from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Todo

router = APIRouter(
    tags=["Todo"],
    prefix="/todo"
)
def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session, Depends(get_db)]

@router.get("/")
async def all_todos(db:db_dependency):
    return db.query(Todo).all()
        
@router.post("/add")
async def add_todo(title: str,db=db_dependency):
    new_todo = Todo( title=title)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@router.put("/update/{id}")
async def update_todo(id: int, title: str, completed:bool, db: db_dependency):
    todo_item = db.query(Todo).filter(Todo.id == id).first()
    todo_item.title = title
    todo_item.completed = completed
    db.commit()
    
@router.delete("/delete/{id}")
async def delete_todo(id:int, db:db_dependency):
    todo_item = db.query(Todo).filter(Todo.id == id).first()
    if todo_item is not None:
        db.delete(todo_item)
    