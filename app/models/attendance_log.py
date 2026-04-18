import uuid
from datetime import datetime, date

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "attendance_date", name="uq_user_attendance_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)
    recognized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="attendance_logs")