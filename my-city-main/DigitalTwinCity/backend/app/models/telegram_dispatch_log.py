from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TelegramDispatchLog(Base):
    __tablename__ = "telegram_dispatch_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_key: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    improvement_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    zone_name: Mapped[str] = mapped_column(String(120), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)