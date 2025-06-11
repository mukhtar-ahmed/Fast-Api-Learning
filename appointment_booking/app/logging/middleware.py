from fastapi import middleware,Request
from app.logging.logger import logger

async def log_middleware(request:Request,call_next):
    log_dict = {
        'url':request.url.path,
        'method':request.method
    }
    logger.info(log_dict)
    response = await call_next(request)
    return response