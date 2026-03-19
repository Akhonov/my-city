from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PriorityAlert(Base):
    __tablename__ = "priority_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=False, index=True)

    improvement_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    priority_score: Mapped[float] = mapped_column(Float, nullable=False)
    priority_level: Mapped[str] = mapped_column(String(20), nullable=False)

    exact_zone_matches_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nearby_similar_requests_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unique_users_nearby_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hotspot_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    ai_beneficial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_benefit_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ai_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    telegram_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )