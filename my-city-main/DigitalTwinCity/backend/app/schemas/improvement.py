from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.simulation import MetricImpact
from app.schemas.suggestion import BenefitAnalysisResponse, HotspotAnalysisResponse


class PlacedImprovementCreate(BaseModel):
    zone_id: int | None = None
    latitude: float
    longitude: float
    improvement_type: str
    title: str | None = None
    description: str | None = None
    source: str = "user"
    user_identifier: str | None = None
    auto_apply: bool = False
    metadata_json: dict[str, Any] | None = None


class PlacedImprovementStatusUpdate(BaseModel):
    status: str


class PlacedImprovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int | None
    improvement_type: str
    latitude: float
    longitude: float
    title: str | None
    description: str | None
    status: str
    source: str
    user_identifier: str | None
    ai_beneficial: bool
    ai_benefit_score: float
    ai_confidence: float
    priority_score: float
    hotspot_score: float
    exact_zone_matches_count: int
    nearby_similar_requests_count: int
    unique_users_nearby_count: int
    explanation: str
    tradeoffs: str
    metric_impacts: str
    metadata_json: str | None
    geometry_type: str
    created_at: datetime
    updated_at: datetime


class PlacedImprovementDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int | None
    improvement_type: str
    latitude: float
    longitude: float
    title: str | None
    description: str | None
    status: str
    source: str
    user_identifier: str | None
    ai_beneficial: bool
    ai_benefit_score: float
    ai_confidence: float
    priority_score: float
    hotspot_score: float
    exact_zone_matches_count: int
    nearby_similar_requests_count: int
    unique_users_nearby_count: int
    explanation: str
    tradeoffs: list[dict[str, Any] | str]
    metric_impacts: list[dict[str, Any]]
    metadata_json: dict[str, Any] | None
    geometry_type: str
    created_at: datetime
    updated_at: datetime


class ImprovementCreateResponse(BaseModel):
    placed_improvement: PlacedImprovementResponse
    benefit_analysis: BenefitAnalysisResponse
    hotspot_analysis: HotspotAnalysisResponse
    priority_score: float
    priority_level: str
    auto_applied: bool
    telegram_triggered: bool


class ImprovementApplyResponse(BaseModel):
    placed_improvement: PlacedImprovementResponse
    before_metrics: dict[str, float]
    after_metrics: dict[str, float]
    metric_impacts: list[MetricImpact]
    before_urban_quality_index: float
    after_urban_quality_index: float
    status: str = Field(default="applied")


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: dict[str, Any]
    properties: dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[GeoJSONFeature]


class ImprovementHotspotRegion(BaseModel):
    improvement_type: str
    zone_id: int | None
    zone_name: str
    center_latitude: float
    center_longitude: float
    object_count: int
    unique_users_count: int
    hotspot_score: float
    priority_level: str