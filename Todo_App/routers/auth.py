from fastapi import APIRouter
router = APIRouter()

@router.get('/hello')
async def read_user():
    return {"message": "Hello, World!"}