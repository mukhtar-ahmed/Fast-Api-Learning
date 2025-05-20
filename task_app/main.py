from fastapi import FastAPI
from models import Base
from database import engine, SessionLocal
import todo,user

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(router=user.router)
app.include_router(router=todo.router)