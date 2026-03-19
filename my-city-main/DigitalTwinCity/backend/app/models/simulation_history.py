from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SimulationHistory(Base):
    __tablename__ = "simulation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    before_metrics: Mapped[str] = mapped_column(Text, nullable=False)
    after_metrics: Mapped[str] = mapped_column(Text, nullable=False)
    metric_impacts: Mapped[str] = mapped_column(Text, nullable=False)

    before_urban_quality_index: Mapped[float] = mapped_column(Float, nullable=False)
    after_urban_quality_index: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)