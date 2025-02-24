from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Todos, Users
from .auth import get_current_user
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
db_user = Annotated[dict, Depends(get_current_user)]

        
@router.get("/todos")
async def read_all_todos(user: db_user, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if user.get('role').casefold() != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    todos = db.query(Todos).all()
    return {
        "total": len(todos),
        "todos": todos
    }
        
@router.delete("/{todo_id}")
async def delete_todo(user: db_user, db: db_dependency, todo_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if user.get('role').casefold() != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting todo")
    return {"message": "Todo deleted"}
    
    
@router.get('/user')
async def get_user(user: db_user, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(Users).filter(Users.id == user.get('id')).first()