from typing import Annotated
from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from sqlalchemy.orm import session
from models import User, Story
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

def get_db():
    db  = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[session , Depends(get_db)]
db_user = Annotated[str, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')


@router.get("/users")
async def get_all_user(user:db_user, db:db_dependency):
    if user is None or user.get("role").casefold() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized")
    return db.query(User).all()

@router.get("/stories")
async def get_all_stories(user:db_user, db:db_dependency):
    if user is None or user.get("role").casefold() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized")
    return db.query(Story).all()

@router.delete('/user/{user_id}')
async def delete_user(user:db_user, db:db_dependency, user_id:int):
    if user is None or user.get("role").casefold() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized")
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user_to_delete)
    db.commit()
    return {"message": "User deleted successfully"}

@router.delete("/story/{story_id}")
async def delete_story(user:db_user, db:db_dependency, story_id:int):
    if user is None or user.get("role").casefold() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized")
    story_to_delete = db.query(Story).filter(Story.id == story_id).first()
    if story_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    db.delete(story_to_delete)
    db.commit()
    return {"message": "Story deleted successfully"}


