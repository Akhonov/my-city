from datetime import datetime

from pydantic import BaseModel

from app.schemas.zone import ZoneMetrics, ZoneResponse


class SimulationRequest(BaseModel):
    action_type: str
    note: str | None = None


class MetricImpact(BaseModel):
    metric: str
    before: float
    after: float
    delta: float


class SimulationResponse(BaseModel):
    zone: ZoneResponse
    action_type: str
    note: str | None
    before_metrics: ZoneMetrics
    after_metrics: ZoneMetrics
    metric_impacts: list[MetricImpact]
    before_urban_quality_index: float
    after_urban_quality_index: float
    created_at: datetime