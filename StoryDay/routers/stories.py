from typing import Annotated
from starlette import status
from fastapi import APIRouter, Depends, HTTPException, Path
from database import SessionLocal
from sqlalchemy.orm import Session
from models import User, Story
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
router = APIRouter(
    prefix='/stories',
    tags=['Stories'],
)

def get_db():
    db  = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class StoryIn(BaseModel):
    day_name :str = Field(title='Day Name', min_length=3)
    description : str = Field(min_length=3)
    intresting : int = Field(gt=0,lt=6)
    new_version : bool = Field(default=True)
    owner_id :int = Field(gt=0)
    
    model_config={
        "json_schema_extra":{
            "message":{
                "day_name": "Monday",
                "description": "Its boring day",
                "intresting": "1",
                "owner_id": "1"
                
            }
        }
    }

@router.get('')
def stories(db: db_dependency):
    return {
        'total': len(db.query(Story).all()),
        'data': db.query(Story).all()
    }
    
@router.get('/{story_id}', status_code=status.HTTP_200_OK)
async def story(db: db_dependency,story_id:int=Path(gt=0)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Not Found")
    return {
        'data': story
    }
    
@router.post('/create_story')
async def create_story(db:db_dependency, story:StoryIn):
    new_story = Story(**story.model_dump())
    db.add(new_story)
    try:
        db.commit()
        db.refresh(new_story)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create story")
    return {
        'message': "Story Added",
        'data':new_story
    }
    
@router.put('/update_story/{story_id}')
async def update_story(db: db_dependency,story_id:int, story:StoryIn):
    found_story = db.query(Story).filter(Story.id == story_id).first()
    if found_story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Not Found")
    found_story.day_name = story.day_name
    found_story.description = story.description
    found_story.intresting = story.intresting
    found_story.new_version = story.new_version
    try:
        db.commit()
        db.refresh(found_story)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update story")
    return {
        'message': "Story Updated",
        'data': found_story
        }
    