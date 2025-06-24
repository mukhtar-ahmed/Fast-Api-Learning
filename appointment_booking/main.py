from fastapi import FastAPI
from app.core.database import Base,engine
from app.auth.router import router as auth_router
from app.todo.todo import router as todo_router
from app.users.router import router as users_router
from app.staff.router import router as staff_router
from app.logging.middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware

Base.metadata.create_all(bind=engine)
# Base.metadata.drop_all(bind=engine)

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware,dispatch=log_middleware)
app.include_router(auth_router,prefix='/api')
app.include_router(users_router,prefix='/api')
app.include_router(staff_router,prefix='/api')
