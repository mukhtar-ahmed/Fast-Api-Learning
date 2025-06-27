from fastapi import APIRouter, HTTPException, status
from app.models.service import Service
from app.schema.service import ServiceOut
from app.dependencies import db_session_dp

router = APIRouter(
    prefix='/services',
    tags=['Services']
)

@router.get('/', response_model=list[ServiceOut], status_code=status.HTTP_200_OK)
async def services(db:db_session_dp):
    all_services =db.query(Service).all()
    return all_services

@router.get('/{id}', response_model=ServiceOut, status_code=status.HTTP_200_OK)
async def service(db:db_session_dp,id:int):
    db_service = db.query(Service).filter(Service.id == id).first()
    if db_service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service Not found")
    return db_service