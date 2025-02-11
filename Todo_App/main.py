from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from fastapi import FastAPI , Depends , HTTPException ,Path
from models import Base, Todos
from database import engine , SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from routers import auth, todos


Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(auth.router)
app.include_router(todos.router)
