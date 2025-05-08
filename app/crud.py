from sqlalchemy import Date, func
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.models.attendence import Attendance
from app.schemas.attendence import AttendanceCreate,AttendenceBase
from datetime import datetime, timezone
from app.security import get_password_hash
from sqlalchemy.exc import SQLAlchemyError


# Utility function to get current UTC time
def get_current_utc_time():
    return datetime.now(timezone.utc)


# Create a new user with hashed password
def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
       hashed_password=user.password,
        role=user.role  # Ensure role is set from schema
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# Get a user by ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# Get all users (for admin)
def get_all_users(db: Session):
    return db.query(User).all()


# Update user (admin functionality)
def update_user(db: Session, user_id: int, user_data: UserCreate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.username = user_data.username
    user.email = user_data.email
    user.password = get_password_hash(user_data.password)
    user.role = user_data.role
    db.commit()
    db.refresh(user)
    return user


# Delete user (admin functionality)
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return True


# Create an attendance record
def create_attendance(db: Session, attendance: AttendanceCreate, user_id: int):
    today = datetime.utcnow().date()
    existing = db.query(Attendance).filter(
        Attendance.user_id == user_id,
        func.date(Attendance.date) == today
    ).first()

    if existing:
        existing.status = attendance.status  # update status
        db.commit()
        db.refresh(existing)
        return {"attendance": existing, "user": existing.user}

    # Otherwise create new
    db_attendance = Attendance(
        user_id=user_id,
        date=datetime.utcnow(),
        status=attendance.status,
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return {"attendance": db_attendance, "user": db_attendance.user}
# Get all attendance records for a user, optionally filtered by date
def get_user_attendance(db: Session, user_id: int, date: datetime = None):
    query = db.query(Attendance).filter(Attendance.user_id == user_id)
    if date:
        query = query.filter(Attendance.date == date)
    return query.all()


# Delete an attendance record
def delete_attendance_record(db: Session, attendance_id: int):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        return None
    db.delete(attendance)
    db.commit()
    return True

