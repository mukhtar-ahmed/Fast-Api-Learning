from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from app.dependencies import db_session_dp,current_user_dp
from app.auth.models.user import StaffProfile, WorkingHour, Service, Role, RoleEnum, Appointment
from app.auth.schema.user import AppointmentIn

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
async def book_appointment(db:db_session_dp,current_user:current_user_dp,appointment_data :AppointmentIn):
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    role_id = current_user.get('role_id')
    if not all([user_id,user_email,role_id]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UNAUTHORIZED User')
    # Check Current user has staff role
    user_role = db.query(Role).filter(Role.id == role_id).first()
    if user_role is None or user_role.name != RoleEnum.client.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not have required permission")
    
    # Check if staff exist 
    db_staff = db.query(StaffProfile).filter(StaffProfile.id == appointment_data.staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    
    # validate Service
    db_service = db.query(Service).filter(Service.staff_id == appointment_data.staff_id, Service.id == appointment_data.service_id).first()
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found for selected staff")
    
    appointment_datetime = datetime.combine(appointment_data.appointment_date, appointment_data.appointment_time)
    
    existing_appointment = db.query(Appointment).filter(Appointment.staff_id == appointment_data.staff_id,Appointment.service_id == appointment_data.service_id, Appointment.appointment_time == appointment_datetime).first()
    if existing_appointment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot already booked")
    
    new_appointment = Appointment(
        client_id=user_id,
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
    
    
    # class AppointmentIn(BaseModel):
    # id: int
    # staff_id:int
    # service_id:int
    # appointment_time:datetime