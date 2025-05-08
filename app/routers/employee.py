import csv
from datetime import date, datetime, timezone
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status,File
from sqlalchemy import Date, func
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app import crud, schemas
from app.models.attendence import Attendance
from app.security import get_current_user
from app.models.user import User
from app.schemas.attendence import AttendanceResponse, AttendenceBase

router = APIRouter()

# Endpoint to get user attendance (employee or admin)
@router.get("/attendance/status/{user_id}", response_model=AttendenceBase)
def get_today_attendance_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = datetime.now(timezone.utc).date()

    attendance = db.query(Attendance).filter(
        Attendance.user_id == user_id,
        func.date(Attendance.date) == today
    ).first()

    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not marked yet.")

    return attendance
