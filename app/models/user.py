from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.enum import RoleEnum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.employee, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships with explicit foreign key specifications
    attendances = relationship("Attendance",foreign_keys="Attendance.user_id",back_populates="user")
    marked_attendances = relationship("Attendance",foreign_keys="Attendance.marked_by",back_populates="marked_by_user")