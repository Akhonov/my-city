from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SuggestionCreate(BaseModel):
    zone_id: int
    latitude: float
    longitude: float
    improvement_type: str
    note: str | None = None
    user_identifier: str


class BenefitMetricImpact(BaseModel):
    metric: str
    delta: float
    direction: str


class BenefitAnalysisResponse(BaseModel):
    beneficial: bool
    benefit_score: float
    confidence: float
    priority_level: str
    zone_need_score: float
    explanation: str
    metric_impacts: list[BenefitMetricImpact]
    tradeoffs: list[str]


class HotspotAnalysisResponse(BaseModel):
    exact_zone_matches_count: int
    nearby_similar_requests_count: int
    unique_users_nearby_count: int
    hotspot_score: float
    is_hotspot: bool
    radius_meters: float


class SuggestionSaved(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    latitude: float
    longitude: float
    improvement_type: str
    note: str | None
    user_identifier: str
    benefit_score: float
    confidence: float
    priority_score: float
    priority_level: str
    beneficial: bool
    exact_zone_matches_count: int
    nearby_similar_requests_count: int
    unique_users_nearby_count: int
    hotspot_score: float
    is_hotspot: bool
    explanation: str
    tradeoffs: str
    metric_impacts: str
    telegram_triggered: bool
    created_at: datetime


class SuggestionResponse(BaseModel):
    suggestion: SuggestionSaved
    benefit_analysis: BenefitAnalysisResponse
    hotspot_analysis: HotspotAnalysisResponse
    priority_score: float
    priority_level: str
    alert_created: bool
    telegram_triggered: bool


class SuggestionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    latitude: float
    longitude: float
    improvement_type: str
    note: str | None
    user_identifier: str
    benefit_score: float
    confidence: float
    priority_score: float
    priority_level: str
    beneficial: bool
    hotspot_score: float
    is_hotspot: bool
    telegram_triggered: bool
    created_at: datetime