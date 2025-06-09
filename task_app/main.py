from fastapi import FastAPI
from database import Base, engine
from router import user,todos
from logger import logger
from fastapi.middleware.cors import CORSMiddleware

# Base.metadata.create_all(bind=engine)
app = FastAPI()

origins =[
    'http://localhost',
    'https://localhost',
    'http://localhost:8000',
    'http://localhost:3000'
    ]

logger.info("Starting API...")

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["GET", "POST", "HEAD", "OPTIONS", "PUT", "DELETE"],
    allow_headers = [ "Access-Control-Allow-Headers",
        "Content-Type", #application/json
        "Authorization", #jwt
        "Access-Control-Allow-Origin",]
)

app.include_router(user.router)
app.include_router(todos.router)
