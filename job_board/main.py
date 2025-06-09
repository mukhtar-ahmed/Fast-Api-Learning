from fastapi import FastAPI, Request
from config import Settings
from router import auth,job_listing,admin,applications
from database import Base,engine
from fastapi.middleware.cors import CORSMiddleware
from logger import logger
from starlette.middleware.base import BaseHTTPMiddleware
from middleware import log_middleware

settings = Settings()
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch =log_middleware )
    
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(job_listing.router)
app.include_router(applications.router)

@app.get("/")
def read_root():
    return {
        "database_url": settings.database_url,
        "debug": settings.debug
    }