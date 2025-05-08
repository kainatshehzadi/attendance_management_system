import csv
from datetime import datetime, timezone
from io import StringIO  # Creating a temporary file without saving in disk
import os  # OS is a built-in module in Python that allows the program to interact with the operating system
from fastapi import APIRouter, Depends, HTTPException, UploadFile, logger, status, File, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app import crud, db, schemas
from app.enum import AttendanceStatusEnum, RoleEnum
from app.models.attendence import Attendance
from app.models.user import User
from app.crud import create_attendance
from app.schemas.attendence import AttendanceCreate, AttendenceBase
from app.schemas.user import UserResponse, UserCreate  
from app.security import get_password_hash
from app.utils import generate_attendance_csv, send_csv_to_email_sync
import logging
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])


# Utility function to check if a user is an admin
def is_admin(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.role == 'admin':
        return True
    return False


# Create a new user (admin only)
@router.post("/create_user", response_model=UserResponse)  
def create_admin_user(user: UserCreate, db: Session = Depends(get_db)):
     db_user = crud.get_user_by_email(db, email=user.email)
     if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists with this email"
        )

    # Check for valid role
     if user.role not in ['admin', 'employee']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role: must be 'admin' or 'employee'"
        )

    # Password match check (if you added `confirm_password`
     if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Hash the password before saving
     user.password = get_password_hash(user.password)
     return crud.create_user(db=db, user=user)

# Get all users (admin only)
@router.get("/users", response_model=list[UserResponse])  
def get_all_users(db: Session = Depends(get_db)):
    return crud.get_all_users(db)


# Get user by ID (admin only)
@router.get("/users/{user_id}", response_model=UserResponse)  
def get_admin_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Update user (admin only)
@router.put("/updateusers/{user_id}", response_model=UserResponse)  
def update_admin_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


# Delete user (admin only)
@router.delete("/deleteusers/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_user(user_id: int, db: Session = Depends(get_db)):
    result = crud.delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
@router.post("/attendance/{user_id}")
def mark_attendance_as_admin(
    user_id: int,
    attendance: AttendanceCreate,
    db: Session = Depends(get_db)
):
    result = create_attendance(db=db, attendance=attendance, user_id=user_id)
    return result

@admin_router.get("/send-attendance/{employee_id}")
def send_attendance_csv(
    employee_id: int,
    status: AttendanceStatusEnum = Query(AttendanceStatusEnum.absent),
    db: Session = Depends(get_db)
):
    try:
        # 1. Validate Employee
        employee = db.query(User).get(employee_id)
        if not employee:
            raise HTTPException(404, "Employee not found")

        # 2. Get/Create Records
        records = db.query(Attendance).filter_by(user_id=employee_id).all()

        if not records:
            admin = db.query(User).filter_by(role=RoleEnum.admin).first()
            if not admin:
                raise HTTPException(500, "No admin user configured")

            default_record = Attendance(
                user_id=employee_id,
                status=status.value,  
                date=datetime.now(timezone.utc),
                marked_by=admin.id
            )
            db.add(default_record)
            db.commit()
            records = [default_record]

        # 3. Prepare Data
        attendance_data = [{
            'date': record.date.isoformat(),
            'status': record.status.value,
            'marked_by': record.marked_by_user.email if record.marked_by_user else "System"
        } for record in records]

        # 4. File Operations
        os.makedirs("attendance_reports", exist_ok=True)
        safe_email = employee.email.replace('@', '_at_').replace('.', '_dot_')
        filename = f"{datetime.now().strftime('%Y%m%d')}_{safe_email}.csv"
        file_path = os.path.join("attendance_reports", filename)

        generate_attendance_csv(file_path, attendance_data)

        # 5. Email
        if os.path.exists(file_path):
            send_csv_to_email_sync(employee.email, file_path)
            return {"message": "Report sent successfully"}

        raise HTTPException(500, "CSV file not created")

    except Exception as e:
        logger.error(f"Endpoint failed: {str(e)}")
        raise HTTPException(500, str(e))
