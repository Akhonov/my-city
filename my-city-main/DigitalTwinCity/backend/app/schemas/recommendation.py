from pydantic import BaseModel


class RecommendationItem(BaseModel):
    zone_id: int
    zone_name: str
    zone_type: str
    action_type: str
    benefit_score: float
    confidence: float
    zone_need_score: float
    estimated_priority_score: float
    explanation: str


class HotspotRegion(BaseModel):
    improvement_type: str
    zone_id: int
    zone_name: str
    center_latitude: float
    center_longitude: float
    suggestion_count: int
    unique_users_count: int
    hotspot_score: float
    priority_level: str


class RecommendationResponse(BaseModel):
    top_recommendations: list[RecommendationItem]
    top_hotspots: list[HotspotRegion]
    most_requested_improvements: list[dict]