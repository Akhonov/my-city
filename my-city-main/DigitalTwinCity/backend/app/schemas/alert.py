from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    improvement_type: str
    latitude: float
    longitude: float
    priority_score: float
    priority_level: str
    exact_zone_matches_count: int
    nearby_similar_requests_count: int
    unique_users_nearby_count: int
    hotspot_score: float
    ai_beneficial: bool
    ai_benefit_score: float
    ai_confidence: float
    summary: str
    recommended_action: str
    telegram_sent: bool
    created_at: datetime
    updated_at: datetime