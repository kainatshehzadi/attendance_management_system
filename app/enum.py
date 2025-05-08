import enum
from enum import Enum
class RoleEnum(str, enum.Enum):
    admin = "admin"
    employee = "employee"
class AttendanceStatusEnum(str, enum.Enum):
    present = "present"
    absent = "Absent"
    late = "Late"  
    half_day = "Half-Day"  