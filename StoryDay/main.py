from fastapi import FastAPI
from models import Base
from database import engine
from fastapi import FastAPI
from routers import auth, stories

Base.metadata.create_all(bind = engine)
app = FastAPI()

app.include_router(auth.router)
app.include_router(stories.router)
