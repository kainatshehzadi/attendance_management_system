from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.enum import AttendanceStatusEnum

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), default=func.now())
    status = Column(Enum(AttendanceStatusEnum), default=AttendanceStatusEnum.absent, nullable=False)
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships with explicit foreign keys
    user = relationship("User",foreign_keys=[user_id],back_populates="attendances")
    marked_by_user = relationship("User",foreign_keys=[marked_by],back_populates="marked_attendances")