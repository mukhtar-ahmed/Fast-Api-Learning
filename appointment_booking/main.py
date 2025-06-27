from fastapi import FastAPI
from app.core.database import Base, engine
from app.auth.router import router as auth_router
from app.role.router import router as role_router
from app.users.router import router as users_router
from app.staff.router import router as staff_router
from app.services.router import router as service_router
from app.appointments.router import router as appointments_router
from app.logging.middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware

Base.metadata.create_all(bind=engine)
# Base.metadata.drop_all(bind=engine)

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware,dispatch=log_middleware)
app.include_router(auth_router,prefix='/api')
app.include_router(role_router,prefix='/api')
app.include_router(users_router,prefix='/api')
app.include_router(staff_router,prefix='/api')
app.include_router(service_router,prefix='/api')
app.include_router(appointments_router,prefix='/api')
