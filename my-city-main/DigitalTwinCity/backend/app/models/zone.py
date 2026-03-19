from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    zone_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    green_area: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lighting: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    traffic: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    air_quality: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    walkability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    accessibility: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    safety: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    heat: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    mobility: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    eco_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    population_density: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    noise_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    public_transport_access: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    barrier_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    housing_capacity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    housing_pressure: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    economic_activity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    commercial_access: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    social_service_access: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    healthcare_access: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    education_access: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    utility_network_load: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    infrastructure_stability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    service_capacity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    attractiveness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    livability_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    employment_support: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    public_space_quality: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    environmental_resilience: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    urban_quality_index: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )