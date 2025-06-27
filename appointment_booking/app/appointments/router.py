from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from app.dependencies import db_session_dp,current_user_dp,require_roles
from app.models.role import RoleEnum
from app.models.user import User
from app.models.staff_profile import StaffProfile
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.working_hour import WorkingHour
from app.schema.appointment import AppointmentIn

router = APIRouter(
    prefix='/appointments',
    tags=['Appointments']
)



@router.get("/staff/{staff_id}/slots/{week_day}")
async def available_slots(db:db_session_dp,staff_id:int,week_day:str,service_id: int):
    # check staff in DB
    db_staff = db.query(StaffProfile).filter(StaffProfile.id == staff_id).first()
    if db_staff is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    # Staff Exist
    # Check Working Hours Exist
    db_staff_working_hours = db.query(WorkingHour).filter(WorkingHour.staff_id == db_staff.id, WorkingHour.day_of_week.ilike(week_day)).first()
    if not db_staff_working_hours:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff Working hours not exist")
    # Working Hours Exist
    # Get Service 
    db_staff_service = db.query(Service).filter(Service.staff_id == db_staff.id, Service.id == service_id).first()
    if not db_staff_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service Not exist")
    # Service Exist
   

    # convert time to datetime for arithematic
    today = datetime.today().date()
    start = datetime.combine(today,db_staff_working_hours.start_time)
    end = datetime.combine(today,db_staff_working_hours.end_time)
    duration = timedelta(minutes=db_staff_service.duration_minutes)
    
    slots = []
    
    while start + duration <= end:
        slots.append(start.time().strftime('%H:%M'))
        start += duration
    
    
    return {
        'day': week_day,
        'slots': slots
    }
    
@router.post("/")
async def book_appointment(db:db_session_dp,appointment_data :AppointmentIn, current_user:dict = require_roles([RoleEnum.client])):
    # Check if staff exist 
    db_staff = db.query(StaffProfile).filter(StaffProfile.id == appointment_data.staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    
    # validate Service
    db_service = db.query(Service).filter(Service.staff_id == appointment_data.staff_id, Service.id == appointment_data.service_id).first()
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found for selected staff")
    
    appointment_datetime = datetime.combine(appointment_data.appointment_date, appointment_data.appointment_time)
    appointment_start = datetime.combine(appointment_data.appointment_date,appointment_data.appointment_time)
    appointment_end = appointment_start + timedelta(minutes=db_service.duration_minutes)
    
    # Check for overlap with existing appointments
    conflicting_appointment = db.query(Appointment).filter(
        Appointment.staff_id == appointment_data.staff_id,
        Appointment.appointment_time < appointment_end,
        (Appointment.appointment_time + timedelta(minutes=db_service.duration_minutes)) > appointment_start
    ).first()
    if conflicting_appointment:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Requested time overlaps with another appointment"
        )
    
    new_appointment = Appointment(
        client_id=current_user.get('id'),
        staff_id=appointment_data.staff_id,
        service_id=appointment_data.service_id,
        appointment_time=appointment_datetime,
        status='booked'
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return {
        "message": "Appointment booked successfully",
        "appointment_id": new_appointment.id,
        "appointment_time": new_appointment.appointment_time.strftime("%Y-%m-%d %H:%M")
    }
    
@router.get('/my')
async def my_appointments(db:db_session_dp,current_user: dict = require_roles([RoleEnum.client])):
    client_appointment = db.query(Appointment).filter(Appointment.client_id == current_user.get('id')).all()
    if not client_appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No appointment booked yet")
    return {
        'total':len(client_appointment),
        'data':client_appointment
    }
    
@router.get('/all')
async def all_appointments(db:db_session_dp,current_user: dict = require_roles([RoleEnum.admin])):
    appointments = db.query(Appointment).all()
    return {
        'total':len(appointments),
        'data':appointments
    }

@router.get('/staff/{id}')
async def staff_appointments(db:db_session_dp,id:int,current_user: dict = require_roles([RoleEnum.admin])):
    # Check if staff exist
    db_staff = db.query(StaffProfile).filter(StaffProfile.id == id).first()
    if not db_staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found"
        )
    
    staff_all_appointments = db.query(Appointment).filter(Appointment.staff_id == id).all()
    if not staff_all_appointments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No appointment found"
        )
    return {
        'total':len(staff_all_appointments),
        'data':staff_all_appointments
    }
    
@router.get('/client/{id}')
async def client_appointments( db:db_session_dp,id:int,current_user: dict = require_roles([RoleEnum.admin])):
    # Check if staff exist
    db_client = db.query(User).filter(User.id == id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )
    
    staff_all_appointments = db.query(Appointment).filter(Appointment.client_id == id).all()
    if not staff_all_appointments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No appointment found"
        )
    return {
        'total':len(staff_all_appointments),
        'data':staff_all_appointments
    }
    
@router.put('/{id}/cancel')
async def cancel_appointment(db:db_session_dp,id:int,current_user: dict = require_roles([RoleEnum.admin])): 
    # Check appointment exist
    db_appointment = db.query(Appointment).filter(Appointment.id == id).first()
    if db_appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment Not found")
    
    db.delete(db_appointment)
    db.commit()
    
    return {
        'message': 'appoitment delete successfullt'
    }
        