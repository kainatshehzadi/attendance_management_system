from pydantic import BaseModel
from typing import List,Literal
from app.enum import AttendanceStatusEnum  # Assuming this Enum exists
from datetime import datetime

# Schema for creating an attendance record
class AttendanceCreate(BaseModel):
    status: AttendanceStatusEnum  # Use Enum for status validation

# Schema for returning an attendance record
class AttendanceResponse(BaseModel):
    status: AttendanceStatusEnum  # Use Enum for status validation
    date: datetime  # Use datetime object for date

    class Config:
        from_attribute = True
class AttendenceBase(BaseModel):
    user_id:int
    date :datetime
    status : Literal["present","absent","leave","half_leave"]
    