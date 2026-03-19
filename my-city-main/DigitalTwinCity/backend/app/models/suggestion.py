from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Suggestion(Base):
    __tablename__ = "suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=False, index=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    improvement_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_identifier: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    benefit_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    priority_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    priority_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    beneficial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    exact_zone_matches_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nearby_similar_requests_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unique_users_nearby_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hotspot_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_hotspot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tradeoffs: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metric_impacts: Mapped[str] = mapped_column(Text, nullable=False, default="")

    telegram_triggered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)