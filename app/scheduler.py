from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
from app.crud import create_attendance, get_user_attendance
from app.db.database import SessionLocal
from sqlalchemy.orm import Session

from app.enum import AttendanceStatusEnum
from app.schemas.attendence import AttendanceCreate

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Task function
def send_attendance_report():
    db: Session = SessionLocal()
    try:
        all_users = db.query(user).all()

        current_time = datetime.now().time()

        for user in all_users:
            # Determine status by time
            if current_time < time(10, 0):  # before 10:00 AM
                status = AttendanceStatusEnum.present
            elif current_time < time(11, 0):  # 10:00-11:00
                status = AttendanceStatusEnum.late
            else:
                status = AttendanceStatusEnum.absent
            
            # Create or update today's attendance
            attendance = AttendanceCreate(status=status)
            create_attendance(db, attendance, user_id=user.id)

        print("Attendance statuses updated based on current time.")

    except Exception as e:
        print(f"Error in attendance scheduler: {e}")
    finally:
        db.close()

# Start scheduler and add job
def start_scheduler():
    scheduler.add_job(send_attendance_report, 'interval', minutes=60) #suppose its generate evey hour
    ''''intervel shows the duration in which its generate report we use corn intead of intervel to specifies duration.like
    cron, week=1 or (cron with quotes ,day_of_week="mon" ,hour=8,minutes=0) it generat a report every mon at 8.00 o'clock '''
    scheduler.start()

